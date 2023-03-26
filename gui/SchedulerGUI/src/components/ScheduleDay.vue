<template>
    <div @click="toggleShift()" class="day-info grid grid-cols-2 gap-1">
        <div class="text-lg font-bold text-center mt-1 mb-1">
            {{ label }}
        </div>
        <div class="text-lg font-bold text-center mt-1 mb-1">
            {{ scheduledShift }}
        </div>
    </div>
</template>
<script setup>
import {ref} from 'vue'
const props = defineProps({
    shifts: Array,
    currentShift: Number,
    dayOfWeek:Number,
    scheduledShift:String
})

const shiftIndex = ref(0)
const selectedShift = ref(props.currentShift || -1)
const label = ref('')

const getShiftsForDay = function(day){
    const results = props.shifts.filter(obj => {
        return obj.day == day;
    });
    return results
}
const toggleShift = function(){
    let currentShifts = getShiftsForDay(props.dayOfWeek)
    shiftIndex.value++
    if(shiftIndex.value >= currentShifts.length){
        shiftIndex.value = 0
    }
    label.value = currentShifts[shiftIndex.value].name
}

</script>
<style scoped>
    .day-info{
        width:100%;
        height:100%;
        user-select: none;
        text-align:center;
    }
    .day-info div{
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .day-info div:first-child{
        border-radius: 2px;
    }

    .day-info div:nth-child(2){
       
    }

</style>