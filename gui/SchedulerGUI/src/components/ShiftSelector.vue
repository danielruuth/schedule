<script setup>
import { useDialog } from 'primevue/usedialog';
import { ref } from 'vue';
import ShiftModal from '../views/modals/shiftsView.vue'
const dialog = useDialog()

const props = defineProps({
  shifts: Array,
  shifts: Array
})

const internalShifts = ref(props.shifts)
const internalExtendedShifts = ref(props.shifts)

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
                <div v-for="shift in internalExtendedShifts" class="text-xs font-thin whitespace-nowrap"><i class="pi pi-circle-fill" :style="{color: `#${shift.color}`, fontSize:'12px'}"></i>&nbsp;{{ shift.name }}&nbsp;({{ shift.start }}&nbsp;-&nbsp;{{ shift.end }})</div>
            </div>
        </div>
        <div class="col-span-1 justify-self-end">
            <span class="pi pi-ellipsis-h right-0 cursor-pointer" @click="openModal($event, 'shift')"></span>
        </div>
    </div>
</template>