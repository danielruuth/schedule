<script setup>
import DateSelector from '../components/DateSelector.vue';
import ResourceSelector from '../components/ResourceSelector.vue';
import ShiftSelector from '../components/ShiftSelector.vue';
import Schedule from '../components/Schedule.vue';
import RuleSelector from '../components/RuleSelector.vue';
import moment from 'moment';
import {ref, toRaw} from 'vue';
import axios from 'axios';
import _ from 'lodash';

/*
Lets load the basics right away
*/

const shifts = ref([
    [3,3],
    [3,3],
    [3,3],
    [3,3],
    [3,2],
    [2,2],
    [2,2]
])

const scheduledShifts = ref([])
const schedulePenalties = ref([])
const scheduleStatus = ref('UNPLANNED')
const scheduleConflicts = ref([])
const showResult = ref(false)

const resources = ref([
    {name: 'Nurse 1'},
    {name: 'Nurse 2'},
    {name: 'Nurse 3'},
    {name: 'Nurse 4'},
    {name: 'Nurse 5'},
    {name: 'Nurse 6'},
    {name: 'Nurse 7'}
])
const startDate = ref( moment().startOf('isoweek').format('YYYY-MM-DD'))
const weeks = ref(4)
const errorMessage = ref(false)

const scheduleRules = ref({
    min_weekends: true,
    health: false
})


const updateShift = function(event){
    console.log(event, 'shifts updated')
}

const updatedDates = function(event){
    console.log(event, 'dates updated')
    weeks.value = event.weeks.value
    startDate.value = event.startDate.value
}

const updatedRules = function(event){
    console.log(event, 'rules updated')
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

const getTotalShifts = function(index){
    let a = getShiftCount(index, 'A')
    let b = getShiftCount(index, 'C')
    return a+b
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

    let buildCoverDemans = (shifts) => {
        let result = []
        shifts.forEach((shift, index)=>{
            if(!result[shift.day-1]){
                result[shift.day-1] = []
            }
            result[shift.day-1].push(shift.resources)
        })
        return result;
    }

   

   let request = {
	"resources": desiredValue(resources.value, 'name'),
	"shifts": ["O", "A", "C"],
    "weeks": weeks.value,
    "fixed_assignments": [],
    "requests": [],
        "shift_constraints":  [
                [0, 1, 1, 0, 2, 2, 0]
        ],

        "cover_demands": toRaw(shifts.value)
    }
    console.log(request)
    const headers = {
      'Content-Type': 'application/json',
   }


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
                <ShiftSelector :shifts="shifts" @onAddedShift="updateShift"/>
            </div>
            <div class="panel">
                <RuleSelector :rules="scheduleRules" @UpdateRules="updatedRules" />
            </div>
        </div>
        <div class="grid">
            <div class="panel">
                <Schedule :startDate="startDate" :weeks="weeks" :resources="resources" :shifts="shifts" :scheduledShifts="scheduledShifts"/>
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
                <span class="text-xs font-bold font-uppercase">Överträdelser:</span>
                {{ schedulePenalties }}
            </div>
        </div>
        <div class="grid grid-cols-10">
            <div class="col-span-8"></div>
            <div class="col-span-2"><Button label="Generera schema" size="small" class="mt-4 float-right" @click="generateSchedule()"/></div>
        </div>
    </div>
</template>