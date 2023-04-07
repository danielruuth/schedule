<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <DynamicDialog />
  <div class="container m-auto grid mt-2 mb-4">
    <img class="place-self-end" srcset="/src/assets/logo-sr@1x.png 1x, /src/assets/logo-sr@2x.png 2x, /src/assets/logo-sr@3x.png 3x" style="width: 70px; height: auto;" />
  </div>
  <div class="container m-auto grid grid-cols-1">
    <RouterView />
  </div>
  
</template>