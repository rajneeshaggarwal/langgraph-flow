// frontend/src/hooks/useKeyPress.ts
import { useEffect, useCallback, useRef, useState } from 'react';

export const useKeyPress = (targetKey: string, handler?: (event: KeyboardEvent) => void, options?: {
  ctrl?: boolean;
  meta?: boolean;
  shift?: boolean;
  alt?: boolean;
  preventDefault?: boolean;
}) => {
  const savedHandler = useRef<(event: KeyboardEvent) => void>();

  useEffect(() => {
    savedHandler.current = handler;
  }, [handler]);

  useEffect(() => {
    const eventHandler = (event: KeyboardEvent) => {
      if (event.key.toLowerCase() === targetKey.toLowerCase()) {
        // Check modifiers if specified
        if (options?.ctrl && !event.ctrlKey) return;
        if (options?.meta && !event.metaKey) return;
        if (options?.shift && !event.shiftKey) return;
        if (options?.alt && !event.altKey) return;

        if (options?.preventDefault) {
          event.preventDefault();
        }

        savedHandler.current?.(event);
      }
    };

    window.addEventListener('keydown', eventHandler);

    return () => {
      window.removeEventListener('keydown', eventHandler);
    };
  }, [targetKey, options]);
};

// Alternative: Simple hook that just returns if key is pressed
export const useIsKeyPressed = (targetKey: string) => {
  const [keyPressed, setKeyPressed] = useState(false);

  useEffect(() => {
    const downHandler = ({ key }: KeyboardEvent) => {
      if (key.toLowerCase() === targetKey.toLowerCase()) {
        setKeyPressed(true);
      }
    };

    const upHandler = ({ key }: KeyboardEvent) => {
      if (key.toLowerCase() === targetKey.toLowerCase()) {
        setKeyPressed(false);
      }
    };

    window.addEventListener('keydown', downHandler);
    window.addEventListener('keyup', upHandler);

    return () => {
      window.removeEventListener('keydown', downHandler);
      window.removeEventListener('keyup', upHandler);
    };
  }, [targetKey]);

  return keyPressed;
};