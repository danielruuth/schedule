import {reactive, ref,watch} from 'vue';
import axios from 'axios';
import moment from 'moment';


import { useLocalStorage } from './localStorage';
export default class ScheduleHandler {
    constructor(){
        this.shifts = ref([])
        this.scheduledShifts = ref([])
        this.schedulePenalties = ref([])
        this.scheduleStatus = ref('UNPLANNED')
        this.scheduleConflicts = ref([])
        this.resources = ref([])
        this.startDate = ref(moment().startOf('isoweek').format('YYYY-MM-DD'))
        this.weeks = ref(4)
        this.errorMessage = ref(false)
        this.rules = ref({
            min_weekends: false,
            health: false
        })
        this.requests = ref([])
        this.assignments = ref([])
        this.__useLocalStorage = false
        this.api_request = ref({})
    }

    set(key, value){
        if(key in this){
            this[key].value = value
            if(this.__useLocalStorage){
                useLocalStorage.set(key, value)
            }
        }else{
            throw new Error('No such key in scheduleHandler')
        }
    }

    get(key, defaultValue){
        if(key in this){
            return this[key].value
        }else{
            throw new Error('No such key in scheduleHandler')
        }
    }

    useLocalStorage(){
        this.__useLocalStorage = true;

        //Try to load from localstorage
        this.shifts.value = useLocalStorage.get('shifts', [
            {
                "name": "A",
                "demand": [
                    3,
                    3,
                    3,
                    3,
                    3,
                    2,
                    2
                ],
                "start": "06:45",
                "end": "16:15"
            },
            {
                "name": "C",
                "demand": [
                    3,
                    3,
                    3,
                    3,
                    2,
                    2,
                    2
                ],
                "start": "14:00",
                "end": "21:00"
            },
            {
                "name": "Verksamhetstid",
                "start": "06:45",
                "end": "16:15",
                "demand": [
                    1,
                    2,
                    0,
                    2,
                    0,
                    0,
                    0
                ]
            }
        ])
        this.resources.value = useLocalStorage.get('resources', [
            {
                "name": "SSK 1"
            },
            {
                "name": "SSK 2"
            },
            {
                "name": "SSK 3"
            },
            {
                "name": "SSK 4"
            },
            {
                "name": "SSK 5"
            },
            {
                "name": "SSK 6"
            },
            {
                "name": "SSK 7"
            },
            {
                "name": "SSK 8"
            },
            {
                "name": "SSK 9"
            },
            {
                "name": "SSK 10"
            },
            {
                "name": "SSK 11"
            }
        ])

        this.rules.value = useLocalStorage.get('rules', {
            min_weekends: false,
            health: false
        })

        this.startDate.value = useLocalStorage.get('startDate', moment().startOf('isoweek').format('YYYY-MM-DD'))
        this.weeks.value = useLocalStorage.get('weeks', 4)

        watch(this.resources.value, async (newValue, oldValue) => {
            useLocalStorage.set('resources', newValue)
        })
        watch(this.weeks, async (newValue, oldValue) => {
            useLocalStorage.set('weeks', newValue)
        })
        watch(this.startDate, async (newValue, oldValue) => {
            console.log('Watching date', newValue)
            useLocalStorage.set('startDate', newValue)
        })
        watch(this.shifts.value, async (newValue, oldValue) => {
            useLocalStorage.set('shifts', newValue)
        })
        watch(this.rules.value, async (newValue, oldValue) => {
            useLocalStorage.set('rules', newValue)
        })
    }

    hasEnoughRestTime(shiftA, shiftB, restTime = 11){
        const restTimeInMilliseconds = restTime * 60 * 60 * 1000; // hours in milliseconds
        const end1 = new Date(`1970-01-01T${shiftA.end}:00.000Z`);
        const start2 = new Date(`1970-01-02T${shiftB.start}:00.000Z`);
        const timeDifference = start2.getTime() - end1.getTime();
        return timeDifference >= restTimeInMilliseconds;
      
    }
      
    getPenalizedTransitions(shifts){
          let penalized = []
          shifts.forEach((shiftA, indexA)=>{
              shifts.forEach((shiftB, indexB)=>{
                  if( !this.hasEnoughRestTime(shiftA, shiftB) ){
                      penalized.push(
                          [indexA+1, indexB+1, 4] //+1 for the "O" off shift that will be unshifted to the array
                      )
                  }
              })
          })
          return penalized;
    }

    fetch(){
        return new Promise((resolve, reject)=>{

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

            this.get('shifts').forEach((item, index)=>{
                shiftsArray.push(item.name)
                item.demand.forEach((cover, day)=>{
                    cover_demands[day][index] = cover
                })
            })
            let request = {
                "resources": desiredValue(this.get('resources'), 'name'),
                "shifts": shiftsArray,
                "weeks": this.get('weeks'),
                "fixed_assignments": this.get('assignments'),
                "requests": this.get('requests'), //Request: (employee, shift, day, weight)
                "shift_constraints":  [ // (shift, hard_min, soft_min, min_penalty,soft_max, hard_max, max_penalty)
                    //One or two consecutive days of rest, this is a hard constraint.
                    [0, 1, 1, 0, 2, 2, 0]
                        
                ],
                "excess_cover_penalties":[2,2,10],
                "weekly_sum_constraints":[
                    //shift, hard_min, soft_min, min_penalty, soft_max, hard_max, max_penalty
                    //TODO: These needs to be generated
                    [0, 1, 2, 7, 2, 3, 4], //Ledig
                    [1,2,2,0,4,5,0],
                    [2,2,2,0,3,4,0]
                    /*[1, 1, 2, 7, 2, 3, 4], //A skift
                    [3, 0, 1, 1, 2, 2, 0], //VT skift
                    [2, 0, 1, 3, 4, 4, 0] // C skift*/
                ],
                "penalized_transitions": [],
                "cover_demands": cover_demands,
                "result_limit": 10
                }

                if(this.get('rules').health == true){
                    request['penalized_transitions'] = this.getPenalizedTransitions(this.get('shifts'))
                }

                const headers = {
                'Content-Type': 'application/json',
            }

            this.api_request.value = request
            
            let apiURL = '/api/getschedule'
            if(import.meta.env.DEV){
                apiURL = 'http://localhost:5000/api/getschedule'
            }
            axios.post(apiURL, request, headers)
            .then((result)=>{
                    const data = result.data

                    if(data.status == 'NOT FEASABLE'){
                        this.set('errorMessage', true);
                        reject('NOT FEASABLE')
                    }else{
                    
                        //Update the data
                        this.set('scheduledShifts', data.result.shifts)
                        this.set('schedulePenalties', data.result.penalties)
                        this.set('scheduleConflicts',data.conflicts)
                        this.set('scheduleStatus', data.status)

                        resolve()
                    }
            })
            .catch((error)=>{
                reject(error)
            })
        })
    }

    parsePenaltyVar(penalty){
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
            throw new Error('Error parsing penalty', e)
        } 
    }
}