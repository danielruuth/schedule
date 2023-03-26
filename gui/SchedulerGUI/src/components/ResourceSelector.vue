<script setup>
import {ref} from 'vue'
import { useDialog } from 'primevue/usedialog';
import ResourceModal from '../views/modals/resourceView.vue'
const dialog = useDialog()

const props = defineProps({
  resources: Array
})

const internalResources = ref(props.resources)

const openModal = function(event, view){
    dialog.open(ResourceModal, {
        props:{
            style: {
                width: '50vw'
            },
        },
        data:{
            resources:internalResources || []
        },
        emits: {
            onAddedResources: (e) => {
                console.log('Emitting', e.value)
                internalResources.value = e.value
            }
        }
    })
}
</script>
<template>
    <div class="grid grid-cols-12">
        <div class="col-span-11">
            <span class="text-xs font-bold uppercase">Resurser: </span>
            <span class="text-xs font-thin">{{internalResources.length}} resurser</span>
        </div>
        <div class="col-span-1 self-end">
            <span class="pi pi-ellipsis-h right-0 cursor-pointer" @click="openModal($event, 'shift')"></span>
        </div>
    </div>
</template>