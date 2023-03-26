<script setup>
import { useDialog } from 'primevue/usedialog';
import { ref } from 'vue';
import ShiftModal from '../views/modals/shiftsView.vue'
const dialog = useDialog()

const props = defineProps({
  shifts: Array
})

const internalShifts = ref(props.shifts)

const openModal = function(event, view){
    dialog.open(ShiftModal,{
        props:{
            style: {
                width: '50vw'
            },
        },
        data:{
            shifts:internalShifts || []
        },
        emits: {
            onAddedShift: (e) => {
                internalShifts.value = e.value
            }
        }
    })
}
</script>
<template>
    <div class="grid grid-cols-12">
        <div class="col-span-11">
            <span class="text-xs font-bold uppercase">Skift: </span>
            <span class="text-xs font-thin">{{ internalShifts[0].length }} skift</span>
        </div>
        <div class="col-span-1 self-end">
            <span class="pi pi-ellipsis-h right-0 cursor-pointer" @click="openModal($event, 'shift')"></span>
        </div>
    </div>
</template>