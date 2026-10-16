const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');

// Only the DOM operations used by this page; network responses stay at the API boundary.
class Element {
    constructor(tag = 'div') {
        this.tagName = tag.toLowerCase();
        this.children = [];
        this.attributes = {};
        this.events = {};
        this.className = '';
        this.ownText = '';
        this.htmlWrites = [];
    }
    set textContent(value) { this.ownText = String(value); this.children = []; }
    get textContent() { return this.ownText + this.children.map(child => child.textContent).join(''); }
    set innerHTML(value) { this.htmlWrites.push(value); this.children = []; this.ownText = ''; }
    append(...children) { this.children.push(...children); }
    appendChild(child) { this.append(child); return child; }
    contains(node) { return this === node || this.children.some(child => child.contains(node)); }
    replaceChildren(...children) {
        if (this.contains(this.ownerDocument?.activeElement)) this.ownerDocument.activeElement = this.ownerDocument.body;
        this.children = children;
        this.ownText = '';
    }
    focus() { this.ownerDocument.activeElement = this; }
    setAttribute(name, value) { this.attributes[name] = String(value); }
    getAttribute(name) { return this.attributes[name]; }
    addEventListener(name, handler) { this.events[name] = handler; }
    querySelectorAll(selector) {
        const matches = node => selector.startsWith('.')
            ? node.className.split(/\s+/).includes(selector.slice(1))
            : node.tagName === selector;
        return this.children.flatMap(child => [...(matches(child) ? [child] : []), ...child.querySelectorAll(selector)]);
    }
    querySelector(selector) { return this.querySelectorAll(selector)[0]; }
}

const source = fs.readFileSync(path.join(__dirname, '../js/history.js'), 'utf8');
function page(listTasks) {
    const elements = { 'task-list': new Element(), 'task-count': new Element('span') };
    const document = {
        body: new Element('body'),
        getElementById: id => elements[id],
        createElement(tag) { const element = new Element(tag); element.ownerDocument = this; return element; },
    };
    document.activeElement = document.body;
    Object.values(elements).forEach(element => { element.ownerDocument = document; });
    const context = vm.createContext({
        document,
        API: { listTasks },
    });
    const ready = Promise.resolve(vm.runInContext(source, context));
    return { list: elements['task-list'], count: elements['task-count'], document, ready };
}
const response = tasks => ({ ok: true, json: async () => ({ tasks }) });
const task = overrides => ({ task_id: 12, title: '高等数学课堂', status: 'success', page_count: 8, created_at: '2026-10-16T08:30:00Z', ...overrides });

test('records display the saved title safely and retain open/export destinations', async () => {
    const title = '<img src=x onerror=alert(1)>课堂记录';
    const env = page(async () => response([task({ title })]));
    await env.ready;
    assert.equal(env.list.querySelector('h3')?.textContent, title);
    assert.equal(env.list.querySelector('img'), undefined);
    assert.equal(env.list.querySelector('.kf-status')?.textContent, '已完成');
    assert.match(env.list.textContent, /8 页/);
    assert.equal(env.count.textContent, '1 条记录');
    assert.deepEqual(env.list.querySelectorAll('a').map(link => link.href), [
        '/outline.html?task_id=12', '/api/tasks/12/export',
    ]);
    assert.equal(env.list.getAttribute('aria-busy'), 'false');
});

test('empty history provides a working route back to upload', async () => {
    const env = page(async () => response([]));
    await env.ready;
    assert.match(env.list.textContent, /还没有整理记录/);
    assert.equal(env.list.querySelector('a')?.href, '/');
    assert.equal(env.count.textContent, '0 条记录');
});

test('failed request offers a retry that replaces the error with fresh records', async () => {
    let attempts = 0;
    const env = page(async () => ++attempts === 1 ? { ok: false } : response([task({ title: '重试后的课堂' })]));
    await env.ready;
    assert.match(env.list.textContent, /无法加载/);
    const retry = env.list.querySelector('button');
    assert.ok(retry, 'the error must have a retry action');
    await retry.events.click();
    assert.equal(env.list.querySelector('h3')?.textContent, '重试后的课堂');
    assert.doesNotMatch(env.list.textContent, /无法加载/);
    assert.equal(env.count.textContent, '1 条记录');
});

for (const [name, failure] of [
    ['network rejection', async () => { throw new Error('offline'); }],
    ['malformed response', async () => ({ ok: true, json: async () => ({ tasks: null }) })],
]) {
    test(`${name} becomes a recoverable error rather than a stuck loading screen`, async () => {
        const env = page(failure);
        await env.ready.catch(() => {});
        assert.match(env.list.textContent, /无法加载/);
        assert.ok(env.list.querySelector('button'));
        assert.equal(env.list.getAttribute('aria-busy'), 'false');
    });
}

test('loading is announced until the pending response is rendered', async () => {
    let finish;
    const env = page(() => new Promise(resolve => { finish = resolve; }));
    assert.equal(env.list.getAttribute('aria-busy'), 'true');
    assert.match(env.list.textContent, /正在读取/);
    finish(response([task()]));
    await env.ready;
    assert.equal(env.list.getAttribute('aria-busy'), 'false');
    assert.equal(env.count.textContent, '1 条记录');
});

test('all known statuses and unknown values remain readable without becoming markup', async () => {
    const statuses = ['pending', 'running', 'success', 'failed', 'partial', '<img src=x>'];
    const env = page(async () => response(statuses.map((status, index) => task({ status, task_id: index + 1 }))));
    await env.ready;
    assert.deepEqual(env.list.querySelectorAll('.kf-status').map(status => status.textContent), [
        '待处理', '处理中', '已完成', '处理失败', '部分完成', '状态未知',
    ]);
    assert.equal(env.list.querySelectorAll('article').length, 6);
    assert.equal(env.list.querySelector('img'), undefined);
});

test('UTC timestamps without an offset from the API retain their instant in a Shanghai browser', async () => {
    const previousTimezone = process.env.TZ;
    process.env.TZ = 'Asia/Shanghai';
    try {
        const env = page(async () => response([task({ created_at: '2026-10-16T08:30:00' })]));
        await env.ready;
        assert.equal(env.list.querySelector('time')?.dateTime, '2026-10-16T08:30:00.000Z');
        assert.match(env.list.querySelector('time')?.textContent, /16:30/);
    } finally {
        if (previousTimezone === undefined) delete process.env.TZ;
        else process.env.TZ = previousTimezone;
    }
});

test('keyboard retry preserves focus on the next available action after repeated failure', async () => {
    const env = page(async () => ({ ok: false }));
    await env.ready;
    const retry = env.list.querySelector('button');
    retry.focus();
    await retry.events.click();
    assert.equal(env.document.activeElement, env.list.querySelector('button'));
});

test('a slow retry does not steal focus after the visitor moves to another control', async () => {
    let attempts = 0;
    let finish;
    const env = page(() => ++attempts === 1 ? Promise.resolve({ ok: false }) : new Promise(resolve => { finish = resolve; }));
    await env.ready;
    const retry = env.list.querySelector('button');
    retry.focus();
    const pending = retry.events.click();
    const outside = env.document.createElement('button');
    outside.focus();
    finish({ ok: false });
    await pending;
    assert.equal(env.document.activeElement, outside);
});
