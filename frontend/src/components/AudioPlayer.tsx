import { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Play, Pause, SkipBack, SkipForward, Volume2, Download } from 'lucide-react';

interface AudioPlayerProps {
  audioUrl: string;
}

const AudioPlayer: React.FC<AudioPlayerProps> = ({ audioUrl }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const audioRef = useRef<HTMLAudioElement>(null);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const updateTime = () => setCurrentTime(audio.currentTime);
    const updateDuration = () => setDuration(audio.duration);

    audio.addEventListener('timeupdate', updateTime);
    audio.addEventListener('loadedmetadata', updateDuration);
    audio.addEventListener('ended', () => setIsPlaying(false));

    return () => {
      audio.removeEventListener('timeupdate', updateTime);
      audio.removeEventListener('loadedmetadata', updateDuration);
      audio.removeEventListener('ended', () => setIsPlaying(false));
    };
  }, []);

  const togglePlay = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const time = parseFloat(e.target.value);
    setCurrentTime(time);
    if (audioRef.current) {
      audioRef.current.currentTime = time;
    }
  };

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const vol = parseFloat(e.target.value);
    setVolume(vol);
    if (audioRef.current) {
      audioRef.current.volume = vol;
    }
  };

  const skip = (seconds: number) => {
    if (audioRef.current) {
      audioRef.current.currentTime += seconds;
    }
  };

  const formatTime = (time: number) => {
    if (isNaN(time)) return '0:00';
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  return (
    <div className="space-y-4">
      <audio ref={audioRef} src={audioUrl} preload="metadata" />

      {/* Waveform Visualization */}
      <div className="h-24 bg-cream border-2 border-ink/10 flex items-center justify-center relative overflow-hidden">
        <div className="absolute inset-0 flex items-center justify-center gap-1 px-4">
          {Array.from({ length: 50 }).map((_, i) => (
            <motion.div
              key={i}
              animate={{
                height: isPlaying ? [20, 60, 20] : 20,
              }}
              transition={{
                duration: 1,
                repeat: isPlaying ? Infinity : 0,
                delay: i * 0.02,
              }}
              className="flex-1 bg-gradient-to-t from-gold-dark to-gold rounded-full"
              style={{
                height: 20 + Math.random() * 40,
                opacity: currentTime / duration > i / 50 ? 1 : 0.3,
              }}
            />
          ))}
        </div>
      </div>

      {/* Progress Bar */}
      <div className="space-y-2">
        <input
          type="range"
          min="0"
          max={duration || 0}
          value={currentTime}
          onChange={handleSeek}
          className="w-full h-2 bg-cream rounded-none appearance-none cursor-pointer accent-gold"
          style={{
            background: `linear-gradient(to right, #d4af37 0%, #d4af37 ${(currentTime / duration) * 100}%, #f5f1e8 ${(currentTime / duration) * 100}%, #f5f1e8 100%)`
          }}
        />
        <div className="flex justify-between text-sm text-gray">
          <span className="font-mono">{formatTime(currentTime)}</span>
          <span className="font-mono">{formatTime(duration)}</span>
        </div>
      </div>

      {/* Controls */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <motion.button
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            onClick={() => skip(-10)}
            className="p-2 bg-cream border border-ink/10 text-ink hover:bg-gold/10 transition-colors"
          >
            <SkipBack className="w-5 h-5" />
          </motion.button>

          <motion.button
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            onClick={togglePlay}
            className="p-4 bg-gradient-to-r from-gold to-gold-dark hover:from-gold-dark hover:to-gold rounded-full text-ink shadow-gold transition-all"
          >
            {isPlaying ? <Pause className="w-6 h-6" /> : <Play className="w-6 h-6 ml-0.5" />}
          </motion.button>

          <motion.button
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            onClick={() => skip(10)}
            className="p-2 bg-cream border border-ink/10 text-ink hover:bg-gold/10 transition-colors"
          >
            <SkipForward className="w-5 h-5" />
          </motion.button>
        </div>

        <div className="flex items-center gap-4">
          {/* Volume Control */}
          <div className="flex items-center gap-2">
            <Volume2 className="w-5 h-5 text-gray" />
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={volume}
              onChange={handleVolumeChange}
              className="w-24 h-2 bg-cream rounded-none appearance-none cursor-pointer accent-gold"
            />
          </div>

          {/* Download Button */}
          <motion.a
            href={audioUrl}
            download="briefing-audio.mp3"
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            className="p-2 bg-cream border border-ink/10 text-ink hover:bg-gold/10 transition-colors"
          >
            <Download className="w-5 h-5" />
          </motion.a>
        </div>
      </div>

      {/* Audio Info */}
      <div className="flex items-center justify-between text-sm text-gray pt-4 border-t-2 border-ink/10">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 bg-gold rounded-full animate-pulse-soft" />
          <span className="font-medium">Professional narration by AWS Polly</span>
        </div>
        <span className="font-mono">2-3 minute briefing</span>
      </div>
    </div>
  );
};

export default AudioPlayer;
