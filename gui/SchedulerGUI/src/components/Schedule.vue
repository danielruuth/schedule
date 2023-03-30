<script setup>
    import ScheduleHeader from './ScheduleHeader.vue';
    import ScheduleRow from './ScheduleRow.vue';
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

</script>
<template>
    <div>
        <ScheduleHeader :startDate="startDate" :weeks="weeks"/>
        <ScheduleRow @updatedRequest="bubbleEvent" :week="weeks" v-for="(resource,index) in resources" :resource="resource" :shifts="shifts" :scheduledShifts="scheduledShifts[index] || []" />
    </div>
</template>