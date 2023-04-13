import {ref} from 'vue';
const ScheduleHandler = {
    extendedShifts: ref([
        {
            name: 'A',
            demand: [3,3,3,3,3,2,2],
            start: "06:45",
            end: "16:15"
        },
        {
            name: 'C',
            demand: [3,3,3,3,2,2,2],
            start: "14:00",
            end: "21:30"
        },
        {
            name: 'Verksamhetstid',
            demand: [1,1,0,1,0,0,0],
            start: "08:00",
            end: "16:30"
        }
    ])
}

export { ScheduleHandler as ScheduleHandler }