<template>
  <div class="app-shell">
    <AppHeader />
    <main>
      <slot />
    </main>
    <footer class="site-footer">
      <div class="page-container site-footer__inner">
        <p>Демонстрационный каркас для кейса РСХБ Цифра</p>
        <p>Точные совпадения появятся после подключения каталога и CV-сервиса.</p>
      </div>
    </footer>
  </div>
</template>
