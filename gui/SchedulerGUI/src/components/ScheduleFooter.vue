<template>
<div class="grid gap-2 grid-cols-12 mt-2 schedule-row">
        
        <div class="col-span-1 resource-name">
            <div v-for="shift in shifts" class="text-xs font-bold">
                {{ shift.name }}
            </div>
        </div>
        <div :class="'col-span-11 grid gap-2 grid-row-1 grid-cols-' + weeks">
            <div v-for="n in weeks">
                <div class="week grid grid-cols-7">
                    <div :class="'day day-info dayIndex-'+ getDayIndex(n, i) +' day-' + i" v-for="i in 7">
                        <div v-for="(shift,index) in shifts" class="text-xs font-light text-center">
                            {{ getShiftCountForDay( i, n, shift.name) }}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
<script setup>
    const props = defineProps({
        weeks: Number,
        shifts: Array,
        scheduledShifts:Array
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
        
        if(props.scheduledShifts){
            props.scheduledShifts.forEach((resource)=>{
                if(resource.shifts[day] == shiftName) result++
            })
        }
        return result
    }
</script>