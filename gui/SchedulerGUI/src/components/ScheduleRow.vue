<template>
   
    <div class="grid gap-2 grid-cols-12 mt-2 schedule-row">
        
        <div class="col-span-1 resource-name">
            <span class="text-sm font-bold capitalize">{{ resource.name }}</span>
        </div>
        <div :class="'col-span-11 grid gap-2 grid-rows-1 grid-cols-' + week">
            <div v-for="n in week" class="col-span-1" style="grid-row: 1;">
                <div class="week grid grid-cols-7">
                    <div :class="'day day-' + i" v-for="i in 7">
                        <ScheduleDay @showContextMenu="handleRightClick" :shifts="localShifts" :dayIndex="getDayIndex(n,i)" :scheduledShift="getScheduledShift(n,i, scheduledShifts)" :requestedShift="getRequestedShift(n,i)" :dayOfWeek="i" />
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
<script setup>
import ScheduleDay from './ScheduleDay.vue'
import {ref, computed} from 'vue'
const emit = defineEmits(['requestMenu'])
    const props = defineProps({
        resource:Object,
        week: Number,
        shifts:Array,
        scheduledShifts:Object,
        requestedShifts:Array
    });

    const localShifts = ref(props.shifts)

    const handleRightClick = function(event, data){
        data.resource = props.resource
        emit('requestMenu', event, data)
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

    const getRequestedShift = function(week, day){
        let shift = props.requestedShifts[getDayIndex(week,day)]
        //let shiftObj = props.shifts.filter(item => item.name == shift.shift );
        return shift
    }

    const getScheduledShift = function(week, day, shifts){
        let offset = 0;
        if(week == 1){
            offset = day-1
        }else{
            offset = ((week-1) * 7) + (day-1)
        }
        try{
            let shift = shifts.shifts[offset]
            if(shift=='O'){ 
                let shiftObj = { name:'', color: 'rgba(255,255,255,0)' } 
                shift = shiftObj
            }else{
                console.log('Not offshift')
                //Take shiftdata from props.shifts
                let shiftObj = props.shifts.filter(item => item.name == shift );
                shift = shiftObj[0]
            }
            return shift;
        }catch(error){
            return ''
        }
    }
</script>

<style scoped lang="scss">

.schedule-row{
    height: 54px;
    border-top-left-radius: 24px;
    border-bottom-left-radius: 24px;
    background-color: rgba(0,0,0,.05);
    
    &:nth-child(2n+3){
        background-color: transparent;
    }
}
.week{
    height:100%;
}

.resource-name{
    text-indent: 16px;
    line-height: 48px;
}
    .day{
        display: flex;
        align-items: center;
        flex-direction: column;
        z-index:2;
        height: 100%;
        transition: background-color 0.5s ease;
        cursor: pointer;
        span{
            display: block;
        }

        &.day-6,  &.day-7 {
            background-color: rgba(0,45,15,.1);
        }

        &:hover{
            background-color: rgba(255, 209, 0, 1);
        }
    }
</style>