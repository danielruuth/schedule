<template>
<div class="grid gap-2 grid-cols-12 mt-2 schedule-row">
        
        <div class="col-span-1 resource-name">
            <div v-for="shift in shifts" class="text-xs font-bold text-right" style="margin:4px;">
                {{ shift.name }}
            </div>
        </div>
        <div :class="'col-span-11 grid gap-2 grid-row-1 grid-cols-' + weeks">
            <div v-for="n in weeks" style="grid-row: 1;">
                <div class="week grid grid-cols-7">
                    <div :class="'day day-info dayIndex-'+ getDayIndex(n, i) +' day-' + i" v-for="i in 7">
                        <div v-for="(shift,index) in shifts" class="text-xs font-light text-center" :class="getOffsetWeightClass(shift.name, i, n)">
                            {{ getShiftCountForDay( i, n, shift.name) }}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
<style scoped>
    .met{
        background-color: rgba(172, 209, 175,1);
    }
    .unmet-1{
        background-color: rgba(244, 113, 116, .2);
    }
    .unmet-2{
        background-color: rgba(244, 113, 116, .4);
    }
    .unmet-3{
        background-color: rgba(244, 113, 116, .6);
    }
    .unmet-4{
        background-color: rgba(244, 113, 116, .8);
    }
    .unmet-5{
        background-color: rgba(244, 113, 116, 1);
    }
    .day-info div{
        border-radius: 2px;
        margin: 4px;
    }
</style>
<script setup>
    const props = defineProps({
        weeks: Number,
        shifts: Array,
        scheduledShifts:Array,
        requestedShifts:Array
    })
    
    const getScheduledShift = function(shiftIndex, dayIndex, weekIndex){
        return `${shiftIndex}, ${getDayIndex(weekIndex,dayIndex)}, ${weekIndex}`
    }

    const getDayIndex = function(week, day){
        let offset = 0;
        if(week == 1){
            offset = day-1
        }else{
            offset = ((week-1) * 7) + (day-1)
        }
        return offset
    }

    const getShiftCountForDay = function(dayIndex, weekIndex, shiftName){
        let result = 0;
        let day = getDayIndex(weekIndex, dayIndex)
        let counted = false


        if(props.scheduledShifts){
            props.scheduledShifts.forEach((resource)=>{
                if(resource.shifts[day] == shiftName) result++; counted = true
            })
        }
        if(!counted){
            props.requestedShifts.forEach((resource)=>{
                if(resource[day].shift == shiftName) result++
            })
        }
        
        return result
    }

    const getShiftDemandForDay = function(dayIndex, shiftName){
        return props.shifts.filter((shift)=>{ return shift.name == shiftName })[0].demand[dayIndex-1]
    }

    const getOffsetWeightClass = function(shiftName, dayIndex, weekIndex){
        let need = getShiftDemandForDay(dayIndex, shiftName)
        let scheduled = getShiftCountForDay(dayIndex, weekIndex, shiftName)
        let diff = Math.abs(need-scheduled)
        
        if(diff>0){
            return 'unmet-' + Math.min(diff,5);
        }else{
            return 'met'
        }
    }
</script>