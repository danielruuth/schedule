<script setup>
    import ScheduleHeader from './ScheduleHeader.vue';
    import ScheduleRow from './ScheduleRow.vue';
    import ScheduleFooter from './ScheduleFooter.vue';
    import {ref, watch} from 'vue'

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
                command: (item) => setResourceRequest(item,index+1)
            }
            requests.push(obj)
        })
        
        localShifts.forEach((item,index)=>{
            let obj = {
                label: item.name,
                icon: '',
                value: item.name,
                command: (item) => setResourceRequest(item, index+1, true)
            }
            assignments.push(obj)
        })
        contextMenuOptions.push({
            label: 'Önskemål',
            items: requests,
            icon: 'pi pi-circle-fill'
        })
        contextMenuOptions.push({
            label: 'Fast uppdrag',
            items: assignments,
            icon: 'pi pi-circle-fill'
        })
        contextMenuOptions.push({
            separator: true
        })
        contextMenuOptions.push({
            label: 'Ledig (Veto)',
            value: 'O',
            icon: 'pi pi-ban',
            command: (item) => setResourceRequest({ item:{name:'Ledig (Veto)', value:'O'} },0)
        })
        contextMenuOptions.push({
            label: 'Rensa',
            value: '-1',
            icon: 'pi pi-trash',
            command: (item) => setResourceRequest({ item:{name:'Rensa', value:'DELETE'} },-1)
        })

        return contextMenuOptions
    }

    const setResourceRequest = function(event, index, fixed = false){
        
        //This needs to be sent back to clicked day aswell
        console.log(event, index)

        emit('ResourceRequest', { 
            dayIndex: contextMenuData.value.dayIndex,
            shiftRequest: event.item.value,
            shiftIndex: index,
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

    watch(props.shifts, async (newValue, oldValue) => {
        console.log('Shifts updated')
        shiftsMenu.value = setupContextMenu(newValue)
    })

</script>
<style>

.p-contextmenu .p-menuitem:first-child > .p-menuitem-content .p-menuitem-link .p-menuitem-icon {
    color: #FF6372;
}
.p-contextmenu .p-menuitem:nth-child(2) > .p-menuitem-content .p-menuitem-link .p-menuitem-icon {
    color: #FFD100;
}

.scheduletype-assignment{
        background-color: #FFD100;
        color: #715D03;
    }

    .scheduletype-requested{
        background-color: #FF6372;
        color: #923840;
    }
</style>
<template>
    <div @mouseleave="clearHighlite()">
        <ContextMenu ref="menuElement" :model="shiftsMenu" />
        <ScheduleHeader :startDate="startDate" :weeks="weeks"/>
        <ScheduleRow @requestMenu="handleRightClick" :week="weeks" :requestedShifts="requestedShifts[index]" v-for="(resource,index) in resources" :resource="resource" :shifts="localShifts" :scheduledShifts="scheduledShifts[index] || []" />
        <ScheduleFooter :weeks="weeks" :shifts="shifts" :scheduledShifts="scheduledShifts" :requestedShifts="requestedShifts" />
    </div>
</template>