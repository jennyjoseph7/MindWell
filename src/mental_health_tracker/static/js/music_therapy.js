// Music Therapy JavaScript Implementation

class MusicPlayer {
    constructor() {
        this.audio = new Audio();
        this.isPlaying = false;
        this.currentTrack = null;
        this.playlist = [];
        this.queue = [];
        this.currentIndex = 0;
        this.isRepeat = false;
        this.isShuffle = false;
        this.currentMood = null;
        
        // Initialize playlists
        this.playlists = {
            calm: [
                {
                    id: 'calm1',
                    title: 'Ocean Waves',
                    artist: 'Nature Sounds',
                    src: '/static/music/calm/ocean-waves.mp3',
                    duration: 300
                },
                {
                    id: 'calm2',
                    title: 'Gentle Rain',
                    artist: 'Nature Sounds',
                    src: '/static/music/calm/gentle-rain.mp3',
                    duration: 300
                }
            ],
            happy: [
                {
                    id: 'happy1',
                    title: 'Sunny Day',
                    artist: 'Upbeat Tunes',
                    src: '/static/music/happy/sunny-day.mp3',
                    duration: 180
                }
            ],
            sad: [
                {
                    id: 'sad1',
                    title: 'Melancholy Melody',
                    artist: 'Emotional Tunes',
                    src: '/static/music/sad/melancholy.mp3',
                    duration: 240
                }
            ],
            focus: [
                {
                    id: 'focus1',
                    title: 'Deep Focus',
                    artist: 'Study Music',
                    src: '/static/music/focus/deep-focus.mp3',
                    duration: 300
                }
            ],
            energetic: [
                {
                    id: 'energetic1',
                    title: 'Energy Boost',
                    artist: 'Workout Mix',
                    src: '/static/music/energetic/energy-boost.mp3',
                    duration: 180
                }
            ],
            sleep: [
                {
                    id: 'sleep1',
                    title: 'Sleepy Lullaby',
                    artist: 'Sleep Sounds',
                    src: '/static/music/sleep/lullaby.mp3',
                    duration: 600
                }
            ]
        };

        this.initializeElements();
        this.bindEvents();
        this.setupAudioEvents();
    }

    initializeElements() {
        // Player controls
        this.playButton = document.getElementById('btn-play');
        this.prevButton = document.getElementById('btn-prev');
        this.nextButton = document.getElementById('btn-next');
        this.forwardButton = document.getElementById('btn-forward');
        this.backwardButton = document.getElementById('btn-backward');
        this.repeatButton = document.getElementById('btn-repeat');
        this.shuffleButton = document.getElementById('btn-shuffle');
        
        // Progress elements
        this.progressBar = document.querySelector('.progress-bar-fill');
        this.currentTimeDisplay = document.getElementById('current-time');
        this.totalTimeDisplay = document.getElementById('total-time');
        
        // Track info
        this.trackTitle = document.getElementById('current-track-name');
        this.trackArtist = document.getElementById('current-track-artist');
        
        // Volume control
        this.volumeSlider = document.getElementById('volume-slider');
        
        // Track list and queue
        this.trackList = document.getElementById('track-list');
        this.queueTracks = document.getElementById('queue-tracks');
        
        // Mood buttons
        this.moodButtons = document.querySelectorAll('.mood-button');
        
        // Feedback elements
        this.feedbackArea = document.getElementById('mood-feedback-area');
        this.feedbackForm = document.getElementById('mood-feedback-form');
        this.closeFeedbackButton = document.getElementById('btn-close-feedback');
        this.closeFeedbackXButton = document.getElementById('btn-close-feedback-x');
        this.showFeedbackButton = document.getElementById('btn-show-feedback');
        this.endSessionButton = document.getElementById('btn-end-session');
        
        // Therapy tip elements
        this.therapyTip = document.getElementById('therapy-tip');
        this.refreshTipButton = document.getElementById('btn-refresh-tip');
        
        // Queue management
        this.clearQueueButton = document.getElementById('btn-clear-queue');
    }

    bindEvents() {
        // Player control events
        this.playButton.addEventListener('click', () => this.togglePlay());
        this.prevButton.addEventListener('click', () => this.playPrevious());
        this.nextButton.addEventListener('click', () => this.playNext());
        this.forwardButton.addEventListener('click', () => this.forward(10));
        this.backwardButton.addEventListener('click', () => this.backward(10));
        this.repeatButton.addEventListener('click', () => this.toggleRepeat());
        this.shuffleButton.addEventListener('click', () => this.toggleShuffle());
        
        // Progress bar click
        document.querySelector('.progress').addEventListener('click', (e) => {
            const progressBar = e.currentTarget;
            const clickPosition = e.offsetX / progressBar.offsetWidth;
            this.audio.currentTime = clickPosition * this.audio.duration;
        });
        
        // Volume control
        this.volumeSlider.addEventListener('input', (e) => {
            this.audio.volume = e.target.value / 100;
        });
        
        // Mood button events
        this.moodButtons.forEach(button => {
            button.addEventListener('click', () => {
                const mood = button.dataset.mood;
                this.changeMood(mood);
            });
        });
        
        // Feedback form events
        this.showFeedbackButton.addEventListener('click', () => this.showFeedback());
        this.closeFeedbackButton.addEventListener('click', () => this.hideFeedback());
        this.closeFeedbackXButton.addEventListener('click', () => this.hideFeedback());
        this.feedbackForm.addEventListener('submit', (e) => this.handleFeedbackSubmit(e));
        this.endSessionButton.addEventListener('click', () => this.showFeedback());
        
        // Queue management
        this.clearQueueButton.addEventListener('click', () => this.clearQueue());
        
        // Therapy tip refresh
        this.refreshTipButton.addEventListener('click', () => this.refreshTherapyTip());
    }

    setupAudioEvents() {
        this.audio.addEventListener('timeupdate', () => this.updateProgress());
        this.audio.addEventListener('loadedmetadata', () => this.updateTotalTime());
        this.audio.addEventListener('ended', () => this.handleTrackEnd());
        this.audio.addEventListener('error', (e) => this.handleAudioError(e));
    }

    loadTrack(track) {
        this.currentTrack = track;
        this.audio.src = track.src;
        this.audio.load();
        this.updateTrackInfo();
        this.highlightCurrentTrack();
    }

    togglePlay() {
        if (this.isPlaying) {
            this.audio.pause();
            this.playButton.innerHTML = '<i class="fas fa-play"></i>';
        } else {
            this.audio.play();
            this.playButton.innerHTML = '<i class="fas fa-pause"></i>';
        }
        this.isPlaying = !this.isPlaying;
    }

    playNext() {
        if (this.queue.length > 0) {
            const nextTrack = this.queue.shift();
            this.loadTrack(nextTrack);
            if (this.isPlaying) this.audio.play();
        } else if (this.playlist.length > 0) {
            this.currentIndex = (this.currentIndex + 1) % this.playlist.length;
            this.loadTrack(this.playlist[this.currentIndex]);
            if (this.isPlaying) this.audio.play();
        }
    }

    playPrevious() {
        if (this.playlist.length > 0) {
            this.currentIndex = (this.currentIndex - 1 + this.playlist.length) % this.playlist.length;
            this.loadTrack(this.playlist[this.currentIndex]);
            if (this.isPlaying) this.audio.play();
        }
    }

    forward(seconds = 10) {
        this.audio.currentTime = Math.min(this.audio.currentTime + seconds, this.audio.duration);
    }

    backward(seconds = 10) {
        this.audio.currentTime = Math.max(this.audio.currentTime - seconds, 0);
    }

    toggleRepeat() {
        this.isRepeat = !this.isRepeat;
        this.repeatButton.classList.toggle('active');
        this.audio.loop = this.isRepeat;
    }

    toggleShuffle() {
        this.isShuffle = !this.isShuffle;
        this.shuffleButton.classList.toggle('active');
    }

    changeMood(mood) {
        this.currentMood = mood;
        this.currentIndex = 0;
        this.playlist = this.playlists[mood];
        
        // Update active state of mood buttons
        this.moodButtons.forEach(button => {
            button.classList.toggle('active', button.dataset.mood === mood);
        });
        
        // Load first track of the selected mood
        if (this.playlist && this.playlist.length > 0) {
            this.loadTrack(this.playlist[0]);
        }
        
        // Update track list display
        this.updateTrackList();
    }

    updateProgress() {
        const progress = (this.audio.currentTime / this.audio.duration) * 100;
        this.progressBar.style.width = `${progress}%`;
        this.currentTimeDisplay.textContent = this.formatTime(this.audio.currentTime);
    }

    updateTotalTime() {
        this.totalTimeDisplay.textContent = this.formatTime(this.audio.duration);
    }

    formatTime(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }

    handleTrackEnd() {
        if (this.isRepeat) {
            this.audio.currentTime = 0;
            this.audio.play();
        } else if (this.isShuffle) {
            this.currentIndex = Math.floor(Math.random() * this.playlist.length);
            this.loadTrack(this.playlist[this.currentIndex]);
            if (this.isPlaying) this.audio.play();
        } else {
            this.playNext();
        }
    }

    handleAudioError(e) {
        console.error('Audio error:', e);
        this.showNotification('Error loading audio track', 'error');
    }

    updateTrackInfo() {
        if (this.currentTrack) {
            this.trackTitle.textContent = this.currentTrack.title;
            this.trackArtist.textContent = this.currentTrack.artist;
        }
    }

    highlightCurrentTrack() {
        const trackItems = this.trackList.querySelectorAll('.track-item');
        trackItems.forEach(item => {
            item.classList.toggle('active', item.dataset.id === this.currentTrack?.id);
        });
    }

    updateTrackList() {
        if (!this.currentMood) return;
        
        const playlist = this.playlists[this.currentMood];
        this.trackList.innerHTML = playlist.map((track, index) => `
            <div class="track-item ${index === this.currentIndex ? 'active' : ''}" 
                 data-id="${track.id}">
                <span class="track-number">${index + 1}</span>
                <span class="track-title">${track.title}</span>
                <span class="track-artist">${track.artist}</span>
                <span class="track-duration">${this.formatTime(track.duration)}</span>
            </div>
        `).join('');
    }

    showFeedback() {
        this.feedbackArea.style.display = 'flex';
    }

    hideFeedback() {
        this.feedbackArea.style.display = 'none';
    }

    async handleFeedbackSubmit(e) {
        e.preventDefault();
        
        const formData = new FormData(this.feedbackForm);
        const feedback = {
            finalMood: formData.get('final-mood'),
            effectivenessRating: formData.get('effectiveness-rating'),
            sessionNotes: formData.get('session-notes')
        };
        
        try {
            // Here you would typically send the feedback to your backend
            console.log('Feedback submitted:', feedback);
            this.showNotification('Thank you for your feedback!', 'success');
            this.hideFeedback();
        } catch (error) {
            console.error('Error submitting feedback:', error);
            this.showNotification('Error submitting feedback', 'error');
        }
    }

    clearQueue() {
        this.queue = [];
        this.updateQueueDisplay();
        this.showNotification('Queue cleared', 'success');
    }

    updateQueueDisplay() {
        if (this.queue.length === 0) {
            this.queueTracks.innerHTML = '<p class="text-muted">No tracks in queue</p>';
        } else {
            this.queueTracks.innerHTML = this.queue.map((track, index) => `
                <div class="queue-track">
                    <span>${index + 1}. ${track.title}</span>
                    <button class="btn-remove-queue" data-index="${index}">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            `).join('');
        }
    }

    refreshTherapyTip() {
        const tips = [
            "Listening to music with a tempo similar to your desired heart rate can help regulate your physical and emotional state.",
            "Music therapy can help reduce stress and anxiety by activating the parasympathetic nervous system.",
            "Different musical elements (tempo, rhythm, melody) can influence your mood and energy levels.",
            "Creating a personalized playlist for specific moods can help you better manage your emotions.",
            "Regular music therapy sessions can improve sleep quality and overall well-being."
        ];
        
        const randomTip = tips[Math.floor(Math.random() * tips.length)];
        this.therapyTip.textContent = randomTip;
        this.refreshTipButton.classList.add('rotating');
        
        setTimeout(() => {
            this.refreshTipButton.classList.remove('rotating');
        }, 800);
    }

    showNotification(message, type = 'info') {
        const notificationArea = document.getElementById('notification-area');
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <i class="fas ${this.getNotificationIcon(type)}"></i>
            <span>${message}</span>
            <button class="notification-close">&times;</button>
        `;
        
        notificationArea.appendChild(notification);
        
        // Add close button functionality
        notification.querySelector('.notification-close').addEventListener('click', () => {
            notification.classList.add('notification-hiding');
            setTimeout(() => notification.remove(), 300);
        });
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.classList.add('notification-hiding');
                setTimeout(() => notification.remove(), 300);
            }
        }, 5000);
    }

    getNotificationIcon(type) {
        switch (type) {
            case 'success': return 'fa-check-circle';
            case 'error': return 'fa-exclamation-circle';
            case 'warning': return 'fa-exclamation-triangle';
            default: return 'fa-info-circle';
        }
    }
}

// Initialize the music player when the page loads
document.addEventListener('DOMContentLoaded', () => {
    const player = new MusicPlayer();
});
