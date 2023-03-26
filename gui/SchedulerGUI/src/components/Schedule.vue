<script setup>
    import ScheduleHeader from './ScheduleHeader.vue';
    import ScheduleRow from './ScheduleRow.vue';

    const props = defineProps({
        startDate: String,
        weeks: Number,
        resources: Array,
        shifts: Array,
        scheduledShifts:Array
    })
</script>
<template>
    <div>
        <ScheduleHeader :startDate="startDate" :weeks="weeks"/>
        <ScheduleRow :week="weeks" v-for="(resource,index) in resources" :resource="resource" :shifts="shifts" :scheduledShifts="scheduledShifts[index] || []" />
    </div>
</template>