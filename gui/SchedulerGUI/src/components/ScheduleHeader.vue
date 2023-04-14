<template>
    <div class="grid gap-2 grid-cols-12">
        <div class="col-span-1">
            
        </div>
        <div :class="'col-span-11 grid gap-2 grid-row-1 grid-cols-' + weeks">
            <div v-for="n in weeks">
                <div class="week grid grid-cols-7">
                    <div :class="'day day-info dayIndex-'+ getDayIndex(n, i) +' day-' + i" v-for="i=0 in 7">
                        <span class="text-xs font-light uppercase text-gray-500">{{ getDayFromOffset(n, i-1).format('ddd') }}</span>
                        <span class="text-lg font-bold uppercase">{{ getDayFromOffset(n, i-1).format('DD') }}</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
<script setup>
    import {ref} from 'vue'
    import moment from 'moment'

    const props = defineProps({
        startDate: String,
        weeks: Number
    })

    const getDayIndex = function(week, day){
        let offset = 0;
        if(week == 1){
            offset = day-1
        }else{
            offset = ((week-1) * 7) + (day-1)
        }
        return offset
    }

    const getDayFromOffset = function(week, day){
        let date = moment(props.startDate).clone().add(week-1, 'weeks').add(day, 'days')
        return date
    }

    const startDate = moment(props.startDate)
    const endDate = startDate.clone().add(props.weeks, 'weeks')
</script>

<style scoped lang="scss">
.week{
    
}
    .day{
        display: flex;
        align-items: center;
        flex-direction: column;
        overflow: hidden;
        
        span{
            display: block;
        }

        &.day-6,  &.day-7 {
            background-color: rgba(0,45,15,.1);
        }
    }
</style>