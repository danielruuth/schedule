<script setup>
    import ScheduleHeader from './ScheduleHeader.vue';
    import ScheduleRow from './ScheduleRow.vue';
    import ScheduleFooter from './ScheduleFooter.vue';
    import {ref} from 'vue'

    const menu = ref();
    const emit = defineEmits(['updateRequests'])

    const props = defineProps({
        startDate: String,
        weeks: Number,
        resources: Array,
        shifts: Array,
        scheduledShifts:Array
    })

    const bubbleEvent = function(event){
        emit('updateRequests', event)
    }

    const clearHighlite = function(){
        let highlitedElements = [].slice.call(document.getElementsByClassName( 'day-info'))
        let highlitedElementsLength = highlitedElements.length
        for(let r = 0; r < highlitedElementsLength; r++){
            highlitedElements[r].classList.remove('highlite-row-class')
        }
    }

</script>
<template>
    <div @mouseleave="clearHighlite()">
        <ScheduleHeader :startDate="startDate" :weeks="weeks"/>
        <ScheduleRow @updatedRequest="bubbleEvent" :week="weeks" v-for="(resource,index) in resources" :resource="resource" :shifts="shifts" :scheduledShifts="scheduledShifts[index] || []" />
        <ScheduleFooter :weeks="weeks" :shifts="shifts" :scheduledShifts="scheduledShifts" />
    </div>
</template>