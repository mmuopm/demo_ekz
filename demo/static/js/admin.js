// слайдер на главной и в кабинете, 3 сек
class HeroSlider {
  constructor(root) {
    this.root = root;
    this.slides = [...root.querySelectorAll('.slider-slide')];
    this.interval = parseInt(root.dataset.interval || '3000', 10);
    this.index = 0;
    this.timer = null;
    this.dotsContainer = root.querySelector('[data-slider-dots]');
    this.init();
  }
  init() {
    if (!this.slides.length) return;
    this.buildDots();
    const prevBtn = this.root.querySelector('[data-slider-prev]');
    const nextBtn = this.root.querySelector('[data-slider-next]');
    if (prevBtn) prevBtn.addEventListener('click', () => this.prev());
    if (nextBtn) nextBtn.addEventListener('click', () => this.next());
    this.root.addEventListener('mouseenter', () => this.pause());
    this.root.addEventListener('mouseleave', () => this.play());
    this.show(0);
    this.play();
  }
  buildDots() {
    if (!this.dotsContainer) return;
    this.slides.forEach((_, i) => {
      const b = document.createElement('button');
      b.type = 'button';
      b.addEventListener('click', () => { this.show(i); this.play(); });
      this.dotsContainer.appendChild(b);
    });
    this.dots = [...this.dotsContainer.querySelectorAll('button')];
  }
  show(i) {
    this.index = (i + this.slides.length) % this.slides.length;
    this.slides.forEach((s, n) => s.classList.toggle('active', n === this.index));
    if (this.dots) this.dots.forEach((d, n) => d.classList.toggle('active', n === this.index));
  }
  next() { this.show(this.index + 1); }
  prev() { this.show(this.index - 1); }
  play() { this.pause(); this.timer = setInterval(() => this.next(), this.interval); }
  pause() { if (this.timer) clearInterval(this.timer); }
}
document.querySelectorAll('[data-slider]').forEach((el) => new HeroSlider(el));
