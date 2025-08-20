import confetti from 'canvas-confetti';

export const showConfetti = () => {
    // First burst
    confetti({
        particleCount: 100,
        spread: 70,
        origin: { y: 0.6 },
        colors: ['#ffd700', '#ffa500', '#ff0000', '#00ff00', '#0000ff', '#4b0082', '#ee82ee']
    });

    // Second burst after a small delay
    setTimeout(() => {
        confetti({
            particleCount: 100,
            spread: 70,
            origin: { y: 0.6 },
            colors: ['#ffd700', '#ffa500', '#ff0000', '#00ff00', '#0000ff', '#4b0082', '#ee82ee']
        });
    }, 250);
};
