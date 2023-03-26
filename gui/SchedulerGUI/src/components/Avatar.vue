<script setup>

const props = defineProps({
    label:String
})

</script>
<template>
    <div class="inline-block h-9 w-9 rounded-full bg-amber-500 text-center inline-flex">
        <span class="label">{{ label }}</span>
    </div>
</template>
<style scoped>

.label{
    line-height: 2.25rem;
    text-align: center;
}

</style>