<script setup>
import DateSelector from '../components/DateSelector.vue';
import ResourceSelector from '../components/ResourceSelector.vue';
import ShiftSelector from '../components/ShiftSelector.vue';
import Schedule from '../components/Schedule.vue';
import RuleSelector from '../components/RuleSelector.vue';
import {ref, computed} from 'vue';
import ViewMore from '../components/ViewMore.vue';
import ScheduleHandler from '../plugins/scheduleHandler';
import moment from 'moment';

import CodeView from '../components/codeview.vue';

/*
Lets load the basics right away
*/
const loading = ref(false)
const showResult = ref(false)
const scheduleError = ref(false)


const ScheduleControll = new ScheduleHandler();
ScheduleControll.useLocalStorage()

function updatedDates(event) {
    ScheduleControll.set('weeks', event.weeks.value);
    ScheduleControll.set('startDate', moment(event.startDate.value).startOf('isoweek').format('YYYY-MM-DD'))
}

const updatedRules = function(event){
    ScheduleControll.set('rules', { 
        health: event.health.value,
        min_weekends: event.min_weekends.value,
        group_offshift: event.group_offshift.value
    })
}

const getShiftCount = function(index, shift){
    try{
        let resourceShifts = ScheduleControll.get('scheduledShifts')[index].shifts;
        let c = 0;
        resourceShifts.forEach((shiftType)=>{
            if(shiftType == shift){
                c++
            }
        })
        return c;
    }catch(e){

    }
}


const checkForResourceOnDay = function(request, where){
    let retval = false
    where.forEach((item, index)=>{
        //If same resource and same day
        if( item[0] == request[0] && item[2] == request[2] ){
            retval = { index: index }
        }
    })
    return retval
}

const getCurrentRequest = function(request){
    return checkForResourceOnDay(request, ScheduleControll.get('requests'))
}

const getCurrentFixed = function(request){
    return checkForResourceOnDay(request, ScheduleControll.get('assignments'))
}

const getCurrentByUserAtDay = function(request){
    let requests = getCurrentRequest(request)
    if( requests ){
        return {type: 'REQUEST', data: requests}
    }else{
        let assignment = getCurrentFixed(request)
        if(assignment){
            return {type: 'ASSIGNMENT', data: assignment}
        }else{
            return false
        }
    }

}

const requestedAssignedByUser = computed(()=>{
    let result = []
    
    ScheduleControll.get('resources').forEach((user,index)=>{
        result[index] = []
        for(let r = 0; r < ScheduleControll.get('weeks') * 7; r++){
            result[index][r] = false
        }
    })
    ScheduleControll.get('assignments').forEach((item)=>{
        result[item[0]][item[2]] = {shift: ScheduleControll.get('shifts')[item[1]-1].name, type: 'assignment'} //user.day = shift
    })
    ScheduleControll.get('requests').forEach((item)=>{
        if(item[1] == 0){ //We request day off, this is quite an ugly fix I know
            result[item[0]][item[2]] = {shift: 'O', type: 'requested'}
        }else{
            result[item[0]][item[2]] = {shift: ScheduleControll.get('shifts')[item[1]-1].name, type: 'requested'} //user.day = shift
        }
    })
    
    return result
})

const handleRequestOrFixed = function(request){
    console.log('In handler', request)
    let resourceIndex = ScheduleControll.get('resources').findIndex((element)=>{
        return element.name == request.resource.name
    })
    let shiftIndex = request.shiftIndex
    let newRequest = []
    let currentIndex = false
    
    if(request.shiftRequest == 'DELETE'){
        console.log('DELETE THIS')
        newRequest = [resourceIndex, shiftIndex, request.dayIndex,0]
        let current = getCurrentByUserAtDay(newRequest)
        if(current){
            if(current.type == 'ASSIGNMENT'){
                ScheduleControll.get('assignments').splice(current.data.index, 1);
            }else if(current.type == 'REQUEST'){
                ScheduleControll.get('requests').splice([current.data.index],1);
            }
        }

    }else if(request.type == 'FIXED'){
        newRequest = [resourceIndex, shiftIndex, request.dayIndex]
        currentIndex = getCurrentFixed(newRequest);
        if( currentIndex !== false){
            ScheduleControll.get('assignments')[currentIndex.index] = newRequest
        }else{
            ScheduleControll.get('assignments').push(newRequest)
        }
    }else{
        newRequest = [resourceIndex, shiftIndex, request.dayIndex, -4]
        if(shiftIndex == 0){ //day off
            newRequest[3] = -8 //Request day of overweight shift request
        }
        currentIndex = getCurrentRequest(newRequest)
        if( currentIndex !== false){
            console.log('Resource request updated', newRequest)
            ScheduleControll.get('requests')[currentIndex.index] = newRequest
        }else{
            console.log('Resource request added', newRequest)
            ScheduleControll.get('requests').push(newRequest)
        }
    }
}


const getTotalShifts = function(index){
    try{
        let resourceShifts = ScheduleControll.get('scheduledShifts')[index].shifts;
        let c = 0;
        resourceShifts.forEach((shiftType)=>{
            if(shiftType!='O'){
                c++
            }
        })
        return c;
    }catch(e){
        return 0
    }
}

const weeklySumConstraints = computed(()=>{
    let result = []
    ScheduleControll.get('schedulePenalties').forEach((row)=>{
        try{
            let parsed = ScheduleControll.parsePenaltyVar(row)
            if (parsed.type == 'weekly_sum_constraint'){
                result.push(parsed)
            }
        }catch(error){
            console.log(error)
        }
    })
    return result
})

const excessDemands = computed(()=>{
    let result = []
    ScheduleControll.get('schedulePenalties').forEach((row)=>{
        let parsed = ScheduleControll.parsePenaltyVar(row)
        if (parsed.type == 'excess_demand'){
            result.push(parsed)
        }
    })
    return result
})

const shiftConstraints = computed(()=>{
    let result = []
    ScheduleControll.get('schedulePenalties').forEach((row)=>{
        let parsed = ScheduleControll.parsePenaltyVar(row)
        if (parsed.type == 'shift_constraint'){
            result.push(parsed)
        }
    })
    return result
})

const generateSchedule = function(){
    loading.value = true
    ScheduleControll.fetch()
    .then(()=>{
        loading.value = false
        showResult.value = true
    }).catch((error)=>{
        loading.value = false
        scheduleError.value = true
    })
}

</script>
<style scoped>
.loader{
    position:absolute;
    top:50%;
    left:50%;
    transform:translate(-50%, -50%);
    width: 60px;
    height: 60px;
    padding: 5px;
    z-index: 1000;
    
}

.zebra tr:nth-child(even) td{
    background-color: rgb(201, 201, 201, .4);
}


</style>

<template>
    <div class="grid space-y-8">
        <div class="loader" v-if="loading">
            <ProgressSpinner style="width: 50px; height: 50px" strokeWidth="8" fill="var(--surface-ground)"
        animationDuration=".5s" aria-label="Laddar" />
    </div>
        <Dialog v-model:visible="scheduleError" modal header="Hoppsan" :style="{ width: '50vw' }">
            <p class="font-thin text-md">
               Inga lösningar hittades med dessa inställningar.<br />
            </p>
        </Dialog>
        <div class="grid grid-cols-4 gap-1">
            <div class="panel">
                <DateSelector :startDate="ScheduleControll.get('startDate')" :weeks="ScheduleControll.get('weeks')" @UpdatedDates="updatedDates"/>
            </div>
            <div class="panel">
                <ResourceSelector :resources="ScheduleControll.get('resources')"/>
            </div>
            <div class="panel">
                <ShiftSelector :shifts="ScheduleControll.get('shifts')" />
            </div>
            <div class="panel">
                <RuleSelector :rules="ScheduleControll.get('rules')" :shifts="ScheduleControll.get('shifts')" @UpdateRules="updatedRules" />
            </div>
        </div>
        <div class="grid">
            <div class="panel">
                <Schedule @ResourceRequest="handleRequestOrFixed" :startDate="ScheduleControll.get('startDate')" :weeks="ScheduleControll.get('weeks')" :resources="ScheduleControll.get('resources')" :shifts="ScheduleControll.get('shifts')" :requestedShifts="requestedAssignedByUser" :scheduledShifts="ScheduleControll.get('scheduledShifts')"/>
            </div>
            <div class="version font-thin text-xs">v.1.2</div>
        </div>
        <div class="grid grid-cols-3 gap-2" v-if="showResult">
            <div class="panel">
                <span class="text-sm font-bold font-uppercase">Resursfördelning:</span>
                <table class="w-full zebra" cellpadding="2">
                    <thead>
                        <tr>
                            <th class="text-xs font-bold text-left">Resurs</th>
                            <th v-for="shift in ScheduleControll.get('shifts')" class="text-xs font-bold text-left">{{ shift.name }}</th>
                            <th class="text-xs font-bold text-left">Totalt</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="(resource,index) in ScheduleControll.get('resources')">
                            <td class="text-xs font-bold">{{ resource.name }}</td>
                            <td v-for="shift in ScheduleControll.get('shifts')" class="text-xs font-light">{{ getShiftCount(index, shift.name) }}</td>
                            <td class="text-xs font-light"> {{ getTotalShifts(index) }} </td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <div class="panel">
                <span class="text-sm font-bold font-uppercase">Överträdelser:</span> <span class="text-sm font-light font-uppercase">{{ ScheduleControll.get('schedulePenalties').length }}</span>
                <div v-if="ScheduleControll.get('schedulePenalties').length == 0">
                    Inga överträdelser!
                </div>
                <ViewMore v-else>
                    <template #content>
                        <table class="w-full zebra" cellpadding="2" v-if="weeklySumConstraints.length > 0">
                            <thead>
                                <tr>
                                    <th colspan="4" class="text-xs font-bold text-left">Antal skift per vecka</th>
                                </tr>
                                <tr>
                                    <th class="text-xs font-bold text-left">Detaljer</th>
                                    <th class="text-xs font-bold text-left">Resurs</th>
                                    <th class="text-xs font-bold text-left">Skift</th>
                                    <th class="text-xs font-bold text-left">Vecka</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="penalty in weeklySumConstraints">
                                    <td class="text-xs font-thin">{{ penalty.hint }}</td>
                                    <td class="text-xs font-thin">{{ ScheduleControll.get('resources')[penalty.employee].name }}</td>
                                    <td class="text-xs font-thin">{{ ScheduleControll.get('shifts')[penalty.shift-1].name }}</td>
                                    <td class="text-xs font-thin">{{ penalty.week }}</td>
                                </tr>
                            </tbody>
                        </table>
                        <table class="w-full zebra mt-4" cellpadding="2" v-if="excessDemands.length > 0">
                            <thead>
                                <tr>
                                    <th colspan="3" class="text-xs font-bold text-left">Överplanerat skift</th>
                                </tr>
                                <tr>
                                    <th class="text-xs font-bold text-left">Överträdelse</th>
                                    <th class="text-xs font-bold text-left">Skift</th>
                                    <th class="text-xs font-bold text-left">Dag</th>
                                    <th class="text-xs font-bold text-left">Vecka</th>
                                    
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="penalty in excessDemands">
                                    <td class="text-xs font-thin">{{ penalty.type }}</td>
                                    <td class="text-xs font-thin">{{ ScheduleControll.get('shifts')[penalty.shift-1].name }}</td>
                                    <td class="text-xs font-thin">{{ penalty.day }}</td>
                                    <td class="text-xs font-thin">{{ penalty.week }}</td>
                                </tr>
                            </tbody>
                        </table>

                        <table class="w-full zebra mt-4" cellpadding="2" v-if="shiftConstraints.length > 0">
                            <thead>
                                <tr>
                                    <th colspan="3" class="text-xs font-bold text-left">Skift begränsningar</th>
                                </tr>
                                <tr>
                                    <th class="text-xs font-bold text-left">Resurs</th>
                                    <th class="text-xs font-bold text-left">Skift</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="penalty in shiftConstraints">
                                    <td class="text-xs font-thin">{{ penalty.employee }}</td>
                                    <td class="text-xs font-thin">{{ penalty.shift }}</td>
                                </tr>
                            </tbody>
                        </table>
                    </template>
                </ViewMore>
            </div>
            <div class="panel">
                <span class="text-sm font-bold font-uppercase">API anrop:</span>
                <ViewMore v-if="ScheduleControll.api_request != ''">
                    <template #content>
                        <CodeView :code="ScheduleControll.api_request"></CodeView>
                    </template>
                </ViewMore>
            </div>
        </div>
        <div class="grid grid-cols-10 pb-8">
            <div class="col-span-8"></div>
            <div class="col-span-2"><Button :loading="loading" label="Generera schema" size="small" class="mt-4 float-right" @click="generateSchedule()"/></div>
        </div>
    </div>
</template>