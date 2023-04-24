<template>
    <div class="grid gap-2 grid-cols-12">
        <div class="col-span-1">
            
        </div>
        <div :class="'col-span-11 grid gap-2 grid-row-1 grid-cols-' + weeks">
            <div v-for="n in weeks" style="grid-row: 1;">
                <div class="week grid grid-cols-7">
                    <div class="col-span-7 text-xs font-bold mb-2 indent-2"> v. {{ getDayFromOffset(n, i-1).format('w') }}</div>
                    <div :class="'day day-info dayIndex-'+ getDayIndex(n, i) +' day-' + i" v-for="i=0 in 7">
                        <span class="text-xs font-light uppercase text-gray-500">{{ getDayFromOffset(n, i-1).format(getDisplayFormat()) }}</span>
                        <span :class="`${getDateTextSize()} font-bold uppercase`">{{ getDayFromOffset(n, i-1).format('DD') }}</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
<script setup>
    import moment from 'moment/min/moment-with-locales'
    moment.locale('sv')

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

    const getDateTextSize = function(){
        if(props.weeks < 4){
            return 'text-lg';
        }else if(props.weeks < 8 ){
            return 'text-md'
        }else if(props.weeks < 12){
            return 'text-sm'
        }else{
            return 'text-xs'
        }
    }

    const getDisplayFormat = function(){
        if(props.weeks > 4){
            return 'dd'
        }else{
            return 'ddd'
        }
    }

    const startDate = moment(props.startDate)
    const endDate = startDate.clone().add(props.weeks, 'weeks')
</script>

<style scoped lang="scss">
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