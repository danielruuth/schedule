<script setup>
import { useDialog } from 'primevue/usedialog';
import { ref } from 'vue';
import ShiftModal from '../views/modals/shiftsView.vue'
const dialog = useDialog()

const props = defineProps({
  shifts: Array,
  extendedShifts: Array
})

const internalShifts = ref(props.shifts)
const internalExtendedShifts = ref(props.extendedShifts)

const openModal = function(event, view){
    dialog.open(ShiftModal,{
        props:{
            style: {
                width: '50vw'
            },
        },
        data:{
            shifts:internalShifts || [],
            extendedShifts: internalExtendedShifts || []
        },
        emits: {
            onAddedShift: (e) => {
                internalExtendedShifts.value = e.names.value
            }
        }
    })
}
</script>
<template>
    <div class="grid grid-cols-12">
        <div class="col-span-11">
            <span class="text-xs font-bold uppercase">Skift: </span>
            <span class="text-xs font-thin">{{ internalExtendedShifts.length }} skift</span>
            <div>
                <span v-for="shift in internalExtendedShifts" class="mr-1 text-xs font-light">{{ shift.name }}, </span>
            </div>
        </div>
        <div class="col-span-1 self-end">
            <span class="pi pi-ellipsis-h right-0 cursor-pointer" @click="openModal($event, 'shift')"></span>
        </div>
    </div>
</template>