import { useCallback, useEffect, useRef, useState } from "react";

// Microphone recording. start() asks for permission and begins; stop() resolves with the recorded Blob.
export function useRecorder() {
  const [recording, setRecording] = useState(false);
  const [seconds, setSeconds] = useState(0);
  const recorderRef = useRef(null);
  const streamRef = useRef(null);
  const chunksRef = useRef([]);
  const timerRef = useRef(null);

  const release = useCallback(() => {
    clearInterval(timerRef.current);
    streamRef.current?.getTracks().forEach((track) => track.stop()); // turns the mic light off
    streamRef.current = null;
  }, []);

  const start = useCallback(async () => {
    let stream;
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch (err) {
      if (err.name === "NotAllowedError") {
        throw new Error("Microphone access is blocked. Allow it from the lock icon in the address bar.");
      }
      if (err.name === "NotFoundError") throw new Error("No microphone was found on this device.");
      throw new Error("Could not start the microphone.");
    }

    streamRef.current = stream;
    chunksRef.current = [];
    const recorder = new MediaRecorder(stream);
    recorder.ondataavailable = (e) => {
      if (e.data.size > 0) chunksRef.current.push(e.data);
    };
    recorder.start();
    recorderRef.current = recorder;

    setSeconds(0);
    setRecording(true);
    timerRef.current = setInterval(() => setSeconds((s) => s + 1), 1000);
  }, []);

  const stop = useCallback(
    () =>
      new Promise((resolve) => {
        const recorder = recorderRef.current;
        recorder.onstop = () => {
          release();
          setRecording(false);
          resolve(new Blob(chunksRef.current, { type: recorder.mimeType }));
        };
        recorder.stop();
      }),
    [release]
  );

  // leaving the page mid-recording must release the microphone
  useEffect(() => release, [release]);

  return { recording, seconds, start, stop };
}