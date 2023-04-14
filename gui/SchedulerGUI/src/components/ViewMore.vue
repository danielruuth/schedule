<template>
    <div class="wrapper">
        <div class="wrapped" :class="(state == 'down') ? 'down' : ''">
            <slot name="content"></slot>
            <div class="fade"></div>
        </div>
        <div class="grid grid-cols-10 relative" :class="(state == 'up') ? '-top-11' : ''">
            <div class="col-span-4"><hr style="top:15px" class="relative"/></div>
            <div class="col-span-2 text-center">
                <button @click="toggleContent()" class="w-full text-xs font-bold uppercase">
                    <span v-if="state == 'up'">Se mer</span>
                    <span v-else>Dölj</span>
                </button>
            </div>
            <div class="col-span-4"><hr style="top:15px" class="relative"/></div>
        </div>
    </div>
</template>
<script setup>
    import {ref} from 'vue'
    const state = ref('up') 
    const toggleContent = function(){
        if(state.value == 'up'){
            state.value = 'down'
        }else{
            state.value = 'up'
        }
    }
</script>

<style scoped>
    .wrapped{
        max-height: 250px;
        overflow: hidden;
        position: relative;
        transition: max-height 1s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    }

    .wrapped.down{
        max-height: 2000px;
    }

    hr{
        border-top: 2px solid rgba(122,122,122,1);
    }

    .fade{
        position:absolute;
        top:180px;
        background: rgb(255,255,255);
        background: linear-gradient(180deg, rgba(255,255,255,0) 0%, rgba(255,255,255,1) 75%);
        height: 70px;
        width:100%;
    }
    .down .fade{
        display: none;
    }
</style>