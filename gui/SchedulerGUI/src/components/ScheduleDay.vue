<template>
    <ContextMenu ref="menu" :model="shiftsMenu" />
    <div @contextmenu="onDayRightClick" class="day-info grid grid-cols-2 gap-1" :class="(scheduledShift != requestedShift && scheduledShift != '' && requestedShift != '') ? 'request-missmatch' : ''">
        <div class="text-lg font-bold text-center mt-1 mb-1" :class="(requestedShift=='') ? 'col-span-2' : ''"  v-if="scheduledShift != ''">
            {{ scheduledShift }}
        </div>
        <div class="text-lg font-bold text-center mt-1 mb-1" :class="(scheduledShift=='') ? 'col-span-2' : ''" v-if="requestedShift != ''">
            {{ requestedShift }}
        </div>
    </div>
</template>
<script setup>
import {ref} from 'vue'
const props = defineProps({
    shifts: Array,
    dayOfWeek:Number,
    scheduledShift:String,
    dayIndex:Number
})
const menu = ref()
const shiftIndex = ref(0)
const label = ref('')

const requestedShift = ref('')
const emit = defineEmits(['ResourceRequest'])

/*let shiftNames = [
        { label: 'Ledig (Veto)', value: 'O', icon:'pi pi-ban', command: (item) => setResourceRequest(item)},
        { label : 'A-pass', value: 'A', icon:'pi pi-sun', command: (item) => setResourceRequest(item)},
        { label: 'C-pass', value:'C', icon:'pi pi-moon', command: (item) => setResourceRequest(item)},
        { label: 'Natt', value:'N', icon:'pi pi-moon', command: (item) => setResourceRequest(item)},
        { label: 'Skift?', value: 'X', icon:'pi pi-question-circle', command: (item) => setResourceRequest(item)}
    ]*/
    let contextMenuOptions = [{
        label: 'Ledig (Veto)',
        value: 'O',
        icon: 'pi pi-ban',
        command: (item) => setResourceRequest({item:{ label:'Ledig (Veto)', value:'O' }},0)
    }]
    props.shifts.forEach((item,index)=>{
        let obj = {
            label: item.name,
            icon: '',
            value: item.name,
            command: (item) => setResourceRequest(item,index)
        }
        contextMenuOptions.push(obj)
    })
    

    const setResourceRequest = function(event, index){
        console.log('Setting resource request')
        requestedShift.value = event.item.value
        emit('ResourceRequest', { 
            dayIndex: props.dayIndex,
            shiftRequest: event.item.value,
            shiftIndex: index
         })
    }
    
    

    const shiftsMenu = ref(contextMenuOptions);
    
    const onDayRightClick = (event, dayIndex) => {
        menu.value.show(event);
    };

const getShiftsForDay = function(day){
    const results = props.shifts.filter(obj => {
        return obj.day == day;
    });
    return results
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

    .request-missmatch{
        animation-name: color;
        animation-duration: 4s;
        animation-iteration-count: infinite;
    }

    @keyframes color {
    0% {
        background-color: rgba(255,0,0,0)
    }
    50% {
        background-color: rgba(255,0,0,0.9)
    }
    100% {
        background-color: rgba(255,0,0,0)
    }
    }

</style>