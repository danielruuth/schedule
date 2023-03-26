<script setup>
import { useDialog } from 'primevue/usedialog';
import DateModal from '../views/modals/dateView.vue'
import moment from 'moment'
import 'moment/locale/sv'
import {ref, inject, computed} from 'vue'

moment.locale('sv')

const dialog = useDialog()
const emit = defineEmits(['UpdatedDates'])

const props = defineProps({
  startDate: String,
  weeks: Number
})

const internalStartDate = ref(props.startDate)
const internalWeeks = ref(props.weeks)
const periodString = computed(()=>{
    let startDate = moment(internalStartDate.value)
    let endDate = startDate.clone().add(internalWeeks.value, 'weeks')
    return startDate.format('Do MMM') + ' - ' + endDate.format('Do MMM')
})

const openModal = function(event, view){
    const ref = dialog.open(DateModal, {
        props:{
            style: {
                width: '50vw'
            },
        },
        data:{
            weeks: internalWeeks || 4,
            startDate: internalStartDate || moment().format('YYYY-MM-DD')
        },
        emits: {
            onUpdatedDates: (e) => {
                internalStartDate.value = e.startDate.value
                internalWeeks.value = e.weeks.value
                emit('UpdatedDates', e) //Bubble it
            }
        }
    })
}
</script>
<template>
    <div class="grid grid-cols-12">
        <div class="col-span-11">
            <span class="text-xs font-bold uppercase">Tidsperiod: </span>
            <span class="text-xs font-thin">{{ periodString }} ({{ internalWeeks }} veckor)</span>
        </div>
        <div class="col-span-1 self-end">
            <span class="pi pi-ellipsis-h right-0 cursor-pointer" @click="openModal($event, 'shift')"></span>
        </div>
    </div>
</template>