<script setup>
    import ScheduleHeader from './ScheduleHeader.vue';
    import ScheduleRow from './ScheduleRow.vue';
    import ScheduleFooter from './ScheduleFooter.vue';
    import {ref} from 'vue'

    const menu = ref();
    const emit = defineEmits(['ResourceRequest'])

    const props = defineProps({
        startDate: String,
        weeks: Number,
        resources: Array,
        shifts: Array,
        scheduledShifts:Array,
        requestedShifts:Array
    })

    const localShifts = ref(props.shifts)

    

    const clearHighlite = function(){
        let highlitedElements = [].slice.call(document.getElementsByClassName( 'day-info'))
        let highlitedElementsLength = highlitedElements.length
        for(let r = 0; r < highlitedElementsLength; r++){
            highlitedElements[r].classList.remove('highlite-row-class')
        }
    }

    const setupContextMenu = function(localShifts){
        let contextMenuOptions = []
        let requests = []
        let assignments = []

        localShifts.forEach((item,index)=>{
            let obj = {
                label: item.name,
                icon: '',
                value: item.name,
                command: (item) => setResourceRequest(item,index)
            }
            requests.push(obj)
        })
        
        localShifts.forEach((item,index)=>{
            let obj = {
                label: item.name,
                icon: '',
                value: item.name,
                command: (item) => setResourceRequest(item,index, true)
            }
            assignments.push(obj)
        })
        contextMenuOptions.push({
            label: 'Önskemål',
            items: requests
        })
        contextMenuOptions.push({
            label: 'Fast uppdrag',
            items: assignments
        })
        contextMenuOptions.push({
            separator: true
        })
        contextMenuOptions.push({
            label: 'Ledig (Veto)',
            value: 'O',
            icon: 'pi pi-ban',
            command: (item) => setResourceRequest({item:{ label:'Ledig (Veto)', value:'O' }},0)
        })
        contextMenuOptions.push({
            label: 'Rensa',
            value: '-1',
            icon: 'pi pi-trash',
            command: (item) => setResourceRequest({item:{ label:'Rensa', value:'-1' }},0)
        })

        return contextMenuOptions
    }

    const setResourceRequest = function(event, index, fixed = false){
        
        //This needs to be sent back to clicked day aswell
        console.log(event)

        emit('ResourceRequest', { 
            dayIndex: contextMenuData.value.dayIndex,
            shiftRequest: event.item.value,
            shiftIndex: index+1,
            resource: contextMenuData.value.resource,
            type: fixed ? 'FIXED' : 'REQUEST'
            })
    }
    const contextMenuData = ref()
    const handleRightClick = function(event, data){
        contextMenuData.value = data;
        menuElement.value.show(event)
    }



    const shiftsMenu = ref( setupContextMenu(props.shifts) );
    const menuElement = ref(0)

</script>
<template>
    <div @mouseleave="clearHighlite()">
        <ContextMenu ref="menuElement" :model="shiftsMenu" />
        <ScheduleHeader :startDate="startDate" :weeks="weeks"/>
        <ScheduleRow @requestMenu="handleRightClick" :week="weeks" :requestedShifts="requestedShifts[index]" v-for="(resource,index) in resources" :resource="resource" :shifts="localShifts" :scheduledShifts="scheduledShifts[index] || []" />
        <ScheduleFooter :weeks="weeks" :shifts="shifts" :scheduledShifts="scheduledShifts" />
    </div>
</template>