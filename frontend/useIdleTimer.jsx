import { useEffect, useRef } from "react";

export function useIdleTimer() {
    const idleTimeout = useRef(null);
    const hasTriggeredIdle = useRef(false);

    const IDLE_LIMIT_MS = 2 * 60 * 1000; // 2 minutes

    // Called when screen becomes idle
    const triggerIdleMode = () => {
        if (hasTriggeredIdle.current) return;
        hasTriggeredIdle.current = true;

        fetch("/api/idle-start", { method: "POST" })
            .catch(err => console.error("Failed to start idle mode:", err));
    };

    // Called when interacts again
    const resetIdleMode = () => {
        if (hasTriggeredIdle.current) {
            // stop LED show
            fetch("/api/idle-stop", { method: "POST" })
                .catch(err => console.error("Failed to stop idle mode:", err));
        }

        hasTriggeredIdle.current = false;

        // reset timer
        clearTimeout(idleTimeout.current);
        idleTimeout.current = setTimeout(triggerIdleMode, IDLE_LIMIT_MS);
    };

    useEffect(() => {
        // counts as user activity
        const events = ["mousemove", "mousedown", "keydown", "touchstart"];

        events.forEach(evt => window.addEventListener(evt, resetIdleMode));

        // initialize timer
        resetIdleMode();

        return () => {
            clearTimeout(idleTimeout.current);
            events.forEach(evt => window.removeEventListener(evt, resetIdleMode));
        };
    }, []);
}
