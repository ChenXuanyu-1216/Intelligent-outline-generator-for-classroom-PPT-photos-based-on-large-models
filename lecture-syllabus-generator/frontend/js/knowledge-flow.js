(() => {
    const root = document.getElementById("knowledge-flow-home");
    const motionButton = root.querySelector(".kf-motion");
    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
    let playing = !reducedMotion.matches;
    let motionChosen = false;

    function render() {
        root.classList.toggle("kf-paused", !playing);
        root.classList.toggle("kf-playing", playing);
        motionButton.textContent = playing ? "暂停背景" : "播放背景";
        motionButton.setAttribute("aria-pressed", String(!playing));
        motionButton.disabled = false;
    }

    motionButton.addEventListener("click", () => {
        motionChosen = true;
        playing = !playing;
        render();
    });
    reducedMotion.addEventListener("change", () => {
        if (!motionChosen) playing = !reducedMotion.matches;
        render();
    });
    render();
})();
