<script setup>
    import {ref, inject, computed} from 'vue'
   
    const dialogRef = inject('dialogRef')
    const emit = defineEmits(['AddedShift'])

    const weekdays = ref([
        'Måndag',
        'Tisdag',
        'Onsdag',
        'Torsdag',
        'Fredag',
        'Lördag',
        'Söndag'
    ])

    const shiftNames = ref( dialogRef.value.data.extendedShifts || [])

    const saveAndUpdate = function(){
        emit('AddedShift', {names: shiftNames})
        dialogRef.value.close()
    }

    const shift = ref({
        name: '',
        start: '',
        end: ''
    })

    

    const addShift = function(){
        shiftNames.value.push({name: shift.value.name, start: shift.value.start, end: shift.value.end, demand: [0,0,0,0,0,0,0]})
    }

    const number_shifts = computed(()=>{
        return shiftNames.value.length
    })

    const removeShift = function(index){
        shiftNames.value.splice((index), 1)
    }

</script>
<template>

    <div class="grid gap-1 grid-cols-10 gap-x-2">
        <div class="col-span-5">
            <span class="text-xs font-bold uppercase">Namn på skift </span><small class="text-xs font-light">t.ex &quot;A&quot;</small>
            <input type="text" v-model="shift.name" class="form-input rounded-md bg-gray-100 border-transparent w-full"/>
        </div>
        <div class="col-span-2">
            <span class="text-xs font-bold uppercase">Starttid</span>
            <input type="time" v-model="shift.start" class="form-input rounded-md bg-gray-100 border-transparent w-full"/>
        </div>
        <div class="col-span-2">
            <span class="text-xs font-bold uppercase">Sluttid</span>
            <input type="time" v-model="shift.end" class="form-input rounded-md bg-gray-100 border-transparent w-full"/>
        </div>
        <div>
            <span class="text-xs font-bold uppercase">&nbsp; </span>
            <Button label="+" @click="addShift" />
        </div>
        <div class="col-span-10">
            <Chip v-for="(shift,index) in shiftNames" class="mr-1" :label="shift.name" @remove="removeShift(index)" removable />
        </div>
    </div>

   

    <div class="grid gap-1 grid-cols-10 gap-x-2">
        <div class="col-span-10 ">
            <span class="text-xs font-bold uppercase">Antal resurser per dag och skift </span>
            <div v-for="n in 7" class="gap-2 mt-4">
                <span class="text-sm font-bold uppercase">{{ weekdays[n-1] }}</span>
                <div :class="'mt-2 grid gap-2 grid-cols-' + number_shifts">
                    <div v-for="i in number_shifts" class="col-span-1">
                        <span class="text-xs font-bold uppercase">{{ shiftNames[i-1].name }}</span>
                        <input type="number" v-model="shiftNames[i-1].demand[n-1]" class="form-input rounded-md bg-gray-100 border-transparent w-full" />
                    </div>
                </div>
            </div>
        </div>
        
        <div class="col-span-10">
            <Button label="Spara" class="w-full float-right" style="height:42px" @click="saveAndUpdate()" />
        </div>
        
    </div>
</template>