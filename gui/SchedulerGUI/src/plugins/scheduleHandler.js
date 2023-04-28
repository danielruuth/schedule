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
            health: false,
            group_offshift: false,
            custom_rules: []
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
                "excess_penalty":[2,2,2,2,2,2,2],
                "max_shifts":2,
                "max_shifts_penalty":2,
                "min_shifts":2,
                "min_shifts_penalty":2,
                "start": "06:45",
                "end": "16:15",
                "break":"00:45",

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
                "excess_penalty":[2,2,2,2,2,2,2],
                "max_shifts":2,
                "max_shifts_penalty":2,
                "min_shifts":2,
                "min_shifts_penalty":2,
                "start": "14:00",
                "end": "21:00",
                "break":"00:30"
            },
            {
                "name": "Verksamhetstid",
                "start": "06:45",
                "end": "16:15",
                "break":"00:45",
                "demand": [
                    1,
                    2,
                    0,
                    2,
                    0,
                    0,
                    0
                ],
                "excess_penalty":[2,2,2,2,2,2,2],
                "max_shifts":2,
                "max_shifts_penalty":2,
                "min_shifts":2,
                "min_shifts_penalty":2,
            }
        ])

        //
        let temp = []
        this.shifts.value.forEach((shift,index)=>{
            if(!shift.excess_penalty || typeof shift.excess_penalty != 'Array'){
                shift['excess_penalty'] = [2,2,2,2,2,2,2]
            }
            if(!shift.max_shifts){
                shift['max_shifts'] = 2
                shift['max_shifts_penalty'] = 1
                shift['min_shifts'] = 2
                shift['min_shifts_penalty'] = 2
            }

            if(!shift.break){
                shift['break'] = "00:45"
            }

            temp.push(shift)
        })
        this.set('shifts', temp)

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
            health: false,
            custom_rules: []
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
        const start1 = new Date(`1970-01-01T${shiftA.start}:00.000Z`)
        let end1 = new Date(`1970-01-01T${shiftA.end}:00.000Z`);

        if(start1.getTime() > end1.getTime()){
            //This means we actually cross midnight, not that we end before we start
            //and we need to fix this ugly style
            end1 = new Date(`1970-01-02T${shiftA.end}:00.000Z`);
        }

        const start2 = new Date(`1970-01-02T${shiftB.start}:00.000Z`);
        const timeDifference = start2.getTime() - end1.getTime();
        return timeDifference >= restTimeInMilliseconds;
    }
      
    getPenalizedTransitions(shifts){
        let penalized = []
        if(this.get('rules').health == true){
            shifts.forEach((shiftA, indexA)=>{
                shifts.forEach((shiftB, indexB)=>{
                    if( !this.hasEnoughRestTime(shiftA, shiftB) ){
                        penalized.push(
                            [indexA+1, indexB+1, 4] //+1 for the "O" off shift that will be unshifted to the array
                        )
                    }
                })
            })
        }else{
            //Dont go from night to day
            shifts.forEach((shiftA, indexA)=>{
                shifts.forEach((shiftB, indexB)=>{
                    if( !this.hasEnoughRestTime(shiftA, shiftB, 8) ){
                        penalized.push(
                            [indexA+1, indexB+1, 4] //+1 for the "O" off shift that will be unshifted to the array
                        )
                    }
                })
            })
        }


        return penalized;
    }

    getExcessCoverPenalties(shifts){
        let res = []
        shifts.forEach((item)=>{
            res.push(item.excess_penalty) //This should be an array representing each day
        })
        return res;
        
    }

    generateSumConstraint(index, shift){
        /*# (shift, hard_min, soft_min, min_penalty, soft_max, hard_max, max_penalty)
        # (3, 0, 1, 3, 4, 4, 0),
        */
        return [
            index,
            shift.min_shifts,
            Math.max(shift.min_shifts-1,0),
            shift.min_shifts_penalty,
            Math.max(shift.max_shifts-1,0),
            shift.max_shifts,
            shift.max_shifts_penalty
        ]
        
    }

    getWeeklySumConstraints(shifts){
        let res = []

        res.push([0, 2, 3, 8, 2, 3, 4]) //Ledig
        
        shifts.forEach((item, index)=>{
            let constraint = this.generateSumConstraint(index+1, item)
            if(constraint){ res.push(constraint) }
        })
        return res;
    }

    getShiftConstraints(){
        let res = []
        if(!this.get('rules').group_offshift){
            res.push(
                [0, 1, 1, 0, 3, 6, 0]
            )
        }else{
            res.push(
                [0, 2, 2, 0, 3, 6, 0]
            )
        }
        return res
    }

    getCoverDemands(shifts){
        let cover_demands = [ //mon->sun
            [],
            [],
            [],
            [],
            [],
            [],
            []
        ]
        shifts.forEach((item, index)=>{
            item.demand.forEach((cover, day)=>{
                cover_demands[day][index] = cover
            })
        })
        return cover_demands
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
            this.get('shifts').forEach((item, index)=>{
                shiftsArray.push(item.name)
            })
            
            let request = {
                "resources": desiredValue(this.get('resources'), 'name'),
                "shifts": shiftsArray,
                "weeks": this.get('weeks'),
                "fixed_assignments": this.get('assignments'),
                "requests": this.get('requests'),
                "shift_constraints":  this.getShiftConstraints(),
                "excess_cover_penalties": this.getExcessCoverPenalties(this.get('shifts')),
                "weekly_sum_constraints":this.getWeeklySumConstraints(this.get('shifts')),
                "penalized_transitions": this.getPenalizedTransitions(this.get('shifts')),
                "cover_demands": this.getCoverDemands(this.get('shifts')),
                "max_weekend_shifts":8,
                "result_limit": 15
            }

            const headers = {
                'Content-Type': 'application/json',
            }

            this.set('scheduledShifts', [])
            this.set('schedulePenalties', [])
            this.set('scheduleConflicts',[])
            this.set('scheduleStatus', [])
            

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