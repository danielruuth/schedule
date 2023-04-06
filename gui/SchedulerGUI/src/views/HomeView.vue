<script setup>
import DateSelector from '../components/DateSelector.vue';
import ResourceSelector from '../components/ResourceSelector.vue';
import ShiftSelector from '../components/ShiftSelector.vue';
import Schedule from '../components/Schedule.vue';
import RuleSelector from '../components/RuleSelector.vue';
import moment from 'moment';
import {ref, toRaw, computed} from 'vue';
import axios from 'axios';
import _ from 'lodash';

/*
Lets load the basics right away
*/

const extendedShifts = ref([
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

const scheduledShifts = ref([])
const schedulePenalties = ref([])
const scheduleStatus = ref('UNPLANNED')
const scheduleConflicts = ref([])
const showResult = ref(false)
const shiftNames = ref()

const resources = ref([
    {name: 'SSK 1'},
    {name: 'SSK 2'},
    {name: 'SSK 3'},
    {name: 'SSK 4'},
    {name: 'SSK 5'},
    {name: 'SSK 6'},
    {name: 'SSK 7'}
])
const startDate = ref( moment().startOf('isoweek').format('YYYY-MM-DD'))
const weeks = ref(4)
const errorMessage = ref(false)

const scheduleRules = ref({
    min_weekends: false,
    health: false
})

const scheduleRequests = ref([])

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
    let resourceShifts = scheduledShifts.value[index].shifts;
    let c = 0;
    resourceShifts.forEach((shiftType)=>{
        if(shiftType == shift){
            c++
        }
    })
    return c;
}

const getCurrentRequest = function(request){
    let retval = false
    scheduleRequests.value.forEach((item, index)=>{
        //If same resource and same day
        if( item[0] == request[0] && item[2] == request[2] ){
            retval = { index: index }
        }
    })
    return retval
}

const handleResourceRequests = function(request){
    let resourceIndex = resources.value.findIndex((element)=>{
        return element.name == request.resource.name
    })

    let shiftIndex = request.request.shiftIndex
    let newRequest = [resourceIndex, shiftIndex, request.request.dayIndex, -2]

    if(shiftIndex == 0){ //day off
        newRequest[3] = -4 //Request day of overweight shift request
    }

    const currentIndex = getCurrentRequest(newRequest);

    if( currentIndex !== false){
        scheduleRequests.value[currentIndex.index] = newRequest
    }else{
        console.log('No request for resource on that day in request list')
        scheduleRequests.value.push(newRequest)
    }
}

const getTotalShifts = function(index){
    let a = getShiftCount(index, 'A')
    let b = getShiftCount(index, 'C')
    return a+b
}
const parsedSchedulePenalties = computed(()=>{
    let result = []
    schedulePenalties.value.forEach((row)=>{
        result.push(parsePenaltyVar(row))
    })
    return result
})
const parsePenaltyVar = function(penalty){
    console.log('Penalty=>',penalty)
    try{
        let string = penalty.name
        let regex = /^(\w+)\((\w+)=(\d+), (\w+)=(\d+), (\w+)=(\d+)\)$/;
        let regex2 = /^(\w+)\((\w+)=(\d+), (\w+)=(\d+)/;

        let matches1 = string.match(regex);
        let matches2 = string.match(regex2)

        
        if(matches2){
            let result = {}
            result.type = matches2[1]
            result[matches2[2]] = matches2[3]
            result[matches2[4]] = matches2[5]

            return result
        }else if(matches1){
            let result = {}
            result.type = matches1[1]
            result[matches1[2]] = matches1[3]
            result[matches1[4]] = matches1[5]
            result[matches1[6]] = matches1[7]

            return result
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

const generateSchedule = function(){

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
        "fixed_assignments": [],
        "requests": scheduleRequests.value,
        "shift_constraints":  [
                [0, 1, 1, 0, 2, 2, 0]
        ],
        "penalized_transitions": [],
        "cover_demands": cover_demands
        }

        if(scheduleRules.value.health == true){
            request['penalized_transitions'] = getPenalizedTransitions(extendedShifts.value)
        }

        const headers = {
        'Content-Type': 'application/json',
    }
    
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

    })
    .catch((error)=>{
        console.log(error)
    })

    console.log(request)
}

</script>

<template>
    <div class="grid space-y-8">
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
                <RuleSelector :rules="scheduleRules" @UpdateRules="updatedRules" />
            </div>
        </div>
        <div class="grid">
            <div class="panel">
                <Schedule @updateRequests="handleResourceRequests" :startDate="startDate" :weeks="weeks" :resources="resources" :shifts="extendedShifts" :scheduledShifts="scheduledShifts"/>
            </div>
        </div>
        <div class="grid grid-cols-3 gap-2" v-if="showResult">
            <div class="panel">
                <span class="text-xs font-bold font-uppercase">Resursfördelning:</span>
                <div class="grid grid-cols-4 w-100">
                    <div class="text-sm font-bold">Resurs</div>
                    <div class="text-sm font-bold">A pass</div>
                    <div class="text-sm font-bold">C pass</div>
                    <div class="text-sm font-bold">Totalt</div>
                    <div class="col-span-4 grid grid-cols-4" v-for="(resource,index) in resources">
                        <div>{{ resource.name }}</div>
                        <div>{{ getShiftCount(index, 'A') }}</div>
                        <div>{{ getShiftCount(index, 'C') }}</div>
                        <div> {{ getTotalShifts(index) }} </div>
                    </div>
                </div>
            </div>
            <div class="panel">
                <span class="text-xs font-bold font-uppercase">Överträdelser:</span> <span class="text-xs font-light font-uppercase">{{ schedulePenalties.length }}</span>
                {{ parsedSchedulePenalties }}
            </div>
        </div>
        <div class="grid grid-cols-10">
            <div class="col-span-8"></div>
            <div class="col-span-2"><Button label="Generera schema" size="small" class="mt-4 float-right" @click="generateSchedule()"/></div>
        </div>
    </div>
</template>