<script setup>
import DateSelector from '../components/DateSelector.vue';
import ResourceSelector from '../components/ResourceSelector.vue';
import ShiftSelector from '../components/ShiftSelector.vue';
import Schedule from '../components/Schedule.vue';
import RuleSelector from '../components/RuleSelector.vue';
import moment from 'moment';
import {ref, computed, watch} from 'vue';
import axios from 'axios';
import _ from 'lodash';
import ViewMore from '../components/ViewMore.vue';
import {useLocalStorage} from '../plugins/localStorage'


/*
Lets load the basics right away
*/
const loading = ref(false)

const extendedShifts = ref(useLocalStorage.get('shifts', [
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
        end: "21:00"
    },
    {
        name: 'Verksamhetstid',
        demand: [1,1,0,2,0,0,0],
        start: "08:00",
        end: "16:30"
    }
]))

watch(extendedShifts, async (newValue, oldValue) => {
  console.log('Change happening to shifts')
})


const scheduledShifts = ref([])
const schedulePenalties = ref([])
const scheduleStatus = ref('UNPLANNED')
const scheduleConflicts = ref([])
const showResult = ref(false)

const resources = ref([
    {name: 'Daniel'},
    {name: 'Natalie'},
    {name: 'Rikard'},
    {name: 'Disa'},
    {name: 'Clara'},
    {name: 'Anna H'},
    {name: 'Anna G'},
    {name: 'Jeanette'},
    {name: 'Karin'},
    {name: 'Madeleine'},
    {name: 'Erik'},
    {name: 'Bibbi'}
])
const startDate = ref( moment().startOf('isoweek').format('YYYY-MM-DD'))
const weeks = ref(4)
const errorMessage = ref(false)

const scheduleRules = ref({
    min_weekends: false,
    health: false
})

const scheduleRequests = ref([])
const scheduleFixedAss = ref([])

const updateShift = function(event){
    console.log(event, 'shifts updated')
}

function updatedDates(event) {
    weeks.value = event.weeks.value;
    startDate.value = event.startDate.value;
}

const updatedRules = function(event){
    scheduleRules.value.health = event.health.value
    scheduleRules.value.min_weekends = event.min_weekends.value
}

const getShiftCount = function(index, shift){
    try{
        let resourceShifts = scheduledShifts.value[index].shifts;
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
    return checkForResourceOnDay(request, scheduleRequests.value)
}

const getCurrentFixed = function(request){
    return checkForResourceOnDay(request, scheduleFixedAss.value)
}

const requestedAssignedByUser = computed(()=>{
    let result = []

    resources.value.forEach((user,index)=>{
        result[index] = []
        for(let r = 0; r < weeks.value * 7; r++){
            result[index][r] = false
        }
    })
    //[resourceIndex, shiftIndex, request.dayIndex]
    scheduleFixedAss.value.forEach((item)=>{
        result[item[0]][item[2]] = extendedShifts.value[item[1]-1].name //user.day = shift
    })
    scheduleRequests.value.forEach((item)=>{
        result[item[0]][item[2]] = extendedShifts.value[item[1]-1].name //user.day = shift
    })
    return result
})

const handleRequestOrFixed = function(request){
    console.log('In handler', request)
    let resourceIndex = resources.value.findIndex((element)=>{
        return element.name == request.resource.name
    })
    let shiftIndex = request.shiftIndex
    let newRequest = []
    let currentIndex = false
    if(request.type == 'FIXED'){
        newRequest = [resourceIndex, shiftIndex, request.dayIndex]
        currentIndex = getCurrentFixed(newRequest);
        if( currentIndex !== false){
            console.log('Fixed assignment updated')
            scheduleFixedAss.value[currentIndex.index] = newRequest
        }else{
            console.log('Fixed assignment added')
            scheduleFixedAss.value.push(newRequest)
        }
    }else{
        newRequest = [resourceIndex, shiftIndex, request.dayIndex, -4]
        if(shiftIndex == 0){ //day off
            newRequest[3] = -8 //Request day of overweight shift request
        }
        currentIndex = getCurrentRequest(newRequest)
        if( currentIndex !== false){
            console.log('Resource request updated')
            scheduleRequests.value[currentIndex.index] = newRequest
        }else{
            console.log('Resource request added')
            scheduleRequests.value.push(newRequest)
        }
    }
}


const getTotalShifts = function(index){
    try{
        let resourceShifts = scheduledShifts.value[index].shifts;
        let c = 0;
        resourceShifts.forEach((shiftType)=>{
            c++
        })
        return c;
    }catch(e){
        return 0
    }
}

const weeklySumConstraints = computed(()=>{
    let result = []
    schedulePenalties.value.forEach((row)=>{
        try{
            let parsed = parsePenaltyVar(row)
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
    schedulePenalties.value.forEach((row)=>{
        let parsed = parsePenaltyVar(row)
        if (parsed.type == 'excess_demand'){
            result.push(parsed)
        }
    })
    return result
})

const shiftConstraints = computed(()=>{
    let result = []
    schedulePenalties.value.forEach((row)=>{
        let parsed = parsePenaltyVar(row)
        if (parsed.type == 'shift_constraint'){
            result.push(parsed)
        }
    })
    return result
})

const parsePenaltyVar = function(penalty){
    try{
        let string = penalty.name
        let regex = /^(\w+)\((\w+)=(\d+), (\w+)=(\d+), (\w+)=(\d+)\)/;
        let regex2 = /^(\w+)\((\w+)=(\d+), (\w+)=(\d+)/;

        

        let matches1 = string.match(regex);
        let matches2 = string.match(regex2)

        let hint = string.split(':')[1]

        
        
        if(matches1){
            let result = {}
            result.type = matches1[1]
            result[matches1[2]] = matches1[3]
            result[matches1[4]] = matches1[5]
            result[matches1[6]] = matches1[7]
            result.hint = hint

            return result
        }else if(matches2){
            let result = {}
            result.type = matches2[1]
            result[matches2[2]] = matches2[3]
            result[matches2[4]] = matches2[5]
            result.hint = hint;

            return result
        }else{
            return {
                type: 'raw',
                data: string
            }
        }
        
    }catch(e){
        console.error('Fullfillment error=>', e)
    }  
}



const hasEnoughRestTime = function (shiftA, shiftB, restTime = 11){
  const restTimeInMilliseconds = restTime * 60 * 60 * 1000; // hours in milliseconds
  const end1 = new Date(`1970-01-01T${shiftA.end}:00.000Z`);
  const start2 = new Date(`1970-01-02T${shiftB.start}:00.000Z`);
  const timeDifference = start2.getTime() - end1.getTime();
  return timeDifference >= restTimeInMilliseconds;

}

const getPenalizedTransitions = function(shifts){
    let penalized = []
    shifts.forEach((shiftA, indexA)=>{
        shifts.forEach((shiftB, indexB)=>{
            if( !hasEnoughRestTime(shiftA, shiftB) ){
                penalized.push(
                    [indexA+1, indexB+1, 4] //+1 for the "O" off shift that will be unshifted to the array
                )
                console.log(`För lite vilotid mellan skift ${shiftA.name} och ${shiftB.name}`)
            }
        })
    })
    console.log('Penalized shifts', penalized)
    return penalized;
}

const penalties = {
    "weekly_sum_constraint":"För många pass/vecka",

}

const generateSchedule = function(){

    loading.value = true

    showResult.value = false;
    let desiredValue = (array,key) => {
        let output = [];
        for (let item of array) {
            output.push(item[key]);
        }
        return output;
    };

   

    let shiftsArray = ['O'] //Off shift
    let cover_demands = [ //mon->sun
        [],
        [],
        [],
        [],
        [],
        [],
        []
    ]

    extendedShifts.value.forEach((item, index)=>{
        shiftsArray.push(item.name)
        item.demand.forEach((cover, day)=>{
            cover_demands[day][index] = cover
        })
    })
    let request = {
        "resources": desiredValue(resources.value, 'name'),
        "shifts": shiftsArray,
        "weeks": weeks.value,
        "fixed_assignments": scheduleFixedAss.value,
        "requests": scheduleRequests.value, //Request: (employee, shift, day, weight)
        "shift_constraints":  [ // (shift, hard_min, soft_min, min_penalty,soft_max, hard_max, max_penalty)
            //One or two consecutive days of rest, this is a hard constraint.
            [0, 1, 1, 0, 2, 2, 0]
                
        ],
        "excess_cover_penalties":[2,2,10],
        "weekly_sum_constraints":[
            //shift, hard_min, soft_min, min_penalty, soft_max, hard_max, max_penalty
            [0, 1, 2, 7, 2, 3, 4], //Ledig
            [1, 1, 2, 7, 2, 3, 4], //A skift
            [3, 0, 1, 1, 2, 2, 0], //VT skift
            [2, 0, 1, 3, 4, 4, 0] // C skift
        ],
        "penalized_transitions": [],
        "cover_demands": cover_demands,
        "result_limit": 10
        }

        if(scheduleRules.value.health == true){
            request['penalized_transitions'] = getPenalizedTransitions(extendedShifts.value)
        }

        const headers = {
        'Content-Type': 'application/json',
    }

    console.log(request)
    
    //axios.post('/api/getschedule', request, headers)
    axios.post('http://localhost:5000/api/getschedule', request, headers)
    .then((result)=>{
            const data = result.data

            if(data.status == 'NOT FEASABLE'){
                errorMessage.value = true;
            }else{
            
                //Update the data
                scheduledShifts.value = data.result.shifts
                schedulePenalties.value = data.result.penalties
                scheduleConflicts.value = data.conflicts
                scheduleStatus.value = data.status

                showResult.value = true
            }
            loading.value = false

    })
    .catch((error)=>{
        console.log(error)
    })

    console.log(request)
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
        <Dialog v-model:visible="errorMessage" modal header="Hoppsan" :style="{ width: '50vw' }">
            <p class="font-thin text-md">
               Inga lösningar hittades med dessa inställningar.<br />
               <span class="font-bold">Tips:</span> Prova att lägga till resurser eller ta bort hälsoschema.
            </p>
        </Dialog>
        <div class="grid grid-cols-4 gap-1">
            <div class="panel">
                <DateSelector :startDate="startDate" :weeks="weeks" @UpdatedDates="updatedDates"/>
            </div>
            <div class="panel">
                <ResourceSelector :resources="resources"/>
            </div>
            <div class="panel">
                <ShiftSelector :extendedShifts="extendedShifts" @AddedShift="updateShift"/>
            </div>
            <div class="panel">
                <RuleSelector :rules="scheduleRules" :shifts="extendedShifts" @UpdateRules="updatedRules" />
            </div>
        </div>
        <div class="grid">
            <div class="panel">
                
                    <Schedule @ResourceRequest="handleRequestOrFixed" :startDate="startDate" :weeks="weeks" :resources="resources" :shifts="extendedShifts" :requestedShifts="requestedAssignedByUser" :scheduledShifts="scheduledShifts"/>
               
            </div>
        </div>
        <div class="grid grid-cols-3 gap-2" v-if="showResult">
            <div class="panel">
                <span class="text-sm font-bold font-uppercase">Resursfördelning:</span>
                <table class="w-full zebra" cellpadding="2">
                    <thead>
                        <tr>
                            <th class="text-xs font-bold text-left">Resurs</th>
                            <th v-for="shift in extendedShifts" class="text-xs font-bold text-left">{{ shift.name }}</th>
                            <th class="text-xs font-bold text-left">Totalt</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="(resource,index) in resources">
                            <td class="text-xs font-bold">{{ resource.name }}</td>
                            <td v-for="shift in extendedShifts" class="text-xs font-light">{{ getShiftCount(index, shift.name) }}</td>
                            <td class="text-xs font-light"> {{ getTotalShifts(index) }} </td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <div class="panel">
                <span class="text-sm font-bold font-uppercase">Överträdelser:</span> <span class="text-sm font-light font-uppercase">{{ schedulePenalties.length }}</span>
                <div v-if="schedulePenalties.length == 0">
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
                                    <td class="text-xs font-thin">{{ resources[penalty.employee].name }}</td>
                                    <td class="text-xs font-thin">{{ extendedShifts[penalty.shift-1].name }}</td>
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
                                    <th class="text-xs font-bold text-left">Vecka</th>
                                    
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="penalty in excessDemands">
                                    <td class="text-xs font-thin">{{ penalty.type }}</td>
                                    <td class="text-xs font-thin">{{ extendedShifts[penalty.shift-1].name }}</td>
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
        </div>
        <div class="grid grid-cols-10 pb-8">
            <div class="col-span-8"></div>
            <div class="col-span-2"><Button label="Generera schema" size="small" class="mt-4 float-right" @click="generateSchedule()"/></div>
        </div>
    </div>
</template>