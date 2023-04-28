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
    const showAdvanced = ref(false)
    const shiftEdit = ref()
    const saveAndUpdate = function(){
        emit('AddedShift', {names: shiftNames})
        dialogRef.value.close()
    }

    const shift = ref({
        name: '',
        start: '',
        end: ''
    })

    
    const cool_colors = [
        '#FFD100',
        '#FF6372',
        '#3D4EDC',
        '#FFEA8B',
        '#FF9BA5',
        '#8C96E6',
        '#D7A900',
        '#D73B4A',
        '#1526B4'
    ]
    const addShift = function(){
        shiftNames.value.push({
            name: shift.value.name, 
            start: shift.value.start, 
            end: shift.value.end,
            break:"00:45", 
            demand: [0,0,0,0,0,0,0], 
            excess_penalty: [2,2,2,2,2,2,2], 
            max_shifts: 2,
            max_shifts_penalty: 2,
            min_shifts: 2,
            min_shifts_penalty: 2,
            color: cool_colors[shiftNames.value.length % 8]
        })
    }

    const number_shifts = computed(()=>{
        return shiftNames.value.length
    })

    const editShift = function(index){
        showAdvanced.value = true
        shiftEdit.value = shiftNames.value[index]
        shiftEdit.value.index = index;
    }

    const saveShift = function(index){
        shiftNames.value[index].color = shiftEdit.value.color
        shiftNames.value[index].name = shiftEdit.value.name
        shiftNames.value[index].start = shiftEdit.value.start
        shiftNames.value[index].end = shiftEdit.value.end
        shiftNames.value[index].break = shiftEdit.value.break
        shiftNames.value[index].demand = shiftEdit.value.demand
        shiftNames.value[index].excess_penalty = shiftEdit.value.excess_penalty
        shiftNames.value[index].max_shifts = shiftEdit.value.max_shifts
        shiftNames.value[index].max_shifts_penalty = shiftEdit.value.max_shifts_penalty
        shiftNames.value[index].min_shifts = shiftEdit.value.min_shifts
        shiftNames.value[index].min_shifts_penalty = shiftEdit.value.min_shifts_penalty

        showAdvanced.value = false
    }

    const deleteShift = function(index){
        console.log('Deleting ', index)
        shiftNames.value.splice(index,1)
        showAdvanced.value = false
    }

</script>
<template>

    <div class="grid gap-1 grid-cols-10 gap-x-2" v-if="!showAdvanced">
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
            <span class="text-xs font-bold uppercase">&nbsp; .</span><br />
            <Button label="+" @click="addShift" style="height:42px;" />
        </div>
        <div class="col-span-10 mt-2 mb-4">
            <Chip v-for="(shift,index) in shiftNames" class="mr-1" @remove="removeShift(index)">
                <i class="pi pi-cog mr-1 cursor-pointer" @click="editShift(index)"></i> {{ shift.name }}
            </Chip>
        </div>
    </div>
    <div v-if="!showAdvanced">
        <div class="grid gap-1 grid-cols-10 gap-x-2">
            <div class="col-span-10 ">
                <span class="text-xs font-bold uppercase">Antal resurser per dag och skift </span>
                <div v-for="n in 7" class="gap-2 mt-4">
                    <span class="text-sm font-bold uppercase">{{ weekdays[n-1] }}</span>
                    <div :class="'mt-2 grid gap-2 grid-cols-' + number_shifts">
                        <div v-for="i in number_shifts" class="col-span-1">
                            <span class="text-xs font-bold uppercase">{{ shiftNames[i-1].name }}</span><br />
                            <input type="number" v-model="shiftNames[i-1].demand[n-1]" class="form-input rounded-md bg-gray-100 border-transparent w-full" />
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="col-span-10 mt-4">
                <Button label="Spara" class="w-full float-right" style="height:42px" @click="saveAndUpdate()" />
            </div>
            
        </div>
    </div>
    <div v-else>
        <span class="text-sm font-bold">Redigera {{ shiftEdit.name }}</span>
        <div class="grid gap-4 grid-cols-10">
            <div>
                <span class="text-xs font-bold uppercase">Färg </span><br />
                <ColorPicker v-model="shiftEdit.color" />
            </div>
            <div class="col-span-3">
                <span class="text-xs font-bold uppercase">Namn på skift </span><small class="text-xs font-light">t.ex &quot;A&quot;</small>
                <input type="text" v-model="shiftEdit.name" class="form-input rounded-md bg-gray-100 border-transparent w-full"/>
            </div>
            <div class="col-span-2">
                <span class="text-xs font-bold uppercase">Starttid</span>
                <input type="time" v-model="shiftEdit.start" class="form-input rounded-md bg-gray-100 border-transparent w-full"/>
            </div>
            <div class="col-span-2">
                <span class="text-xs font-bold uppercase">Sluttid</span>
                <input type="time" v-model="shiftEdit.end" class="form-input rounded-md bg-gray-100 border-transparent w-full"/>
            </div>
            <div class="col-span-2">
                <span class="text-xs font-bold uppercase">Rast</span>
                <input type="time" v-model="shiftEdit.break" class="form-input rounded-md bg-gray-100 border-transparent w-full"/>
            </div>
            <div class="col-span-5 mt-4">
                <span class="text-sm font-bold uppercase">Resursbehov &amp; överbokning </span><br />
                <span class="text-xs font-bold mb-4">Ange straff vid överbokning <small class="font-thin">(0 = Överbokning förbjudet)</small></span>
                <div v-for="n in 7" class="gap-2 mt-1 grid grid-cols-3">
                    <div class="col-span-2">
                        <span class="text-xs font-bold uppercase">{{ weekdays[n-1] }}</span>
                        <input type="number" v-model="shiftEdit.demand[n-1]" class="form-input rounded-md bg-gray-100 border-transparent w-full" />
                    </div>
                    <div>
                        <span class="text-xs font-bold uppercase">Straff</span><br />
                        <input type="number" class="form-input rounded-md bg-gray-100 border-transparent w-full" v-model="shiftEdit.excess_penalty[n-1]"/>
                    </div>
                </div>
            </div>
            <div class="col-span-5 mt-4">
                <span class="text-sm font-bold uppercase">Avancerade inställningar</span><br />
                <div class="grid grid-cols-2 gap-2">
                    <div class="gap-2 mt-1">
                        <span class="text-xs font-bold uppercase">Max skift/vecka</span><br />
                        <input type="number" class="form-input rounded-md bg-gray-100 border-transparent w-full" v-model="shiftEdit.max_shifts" />
                    </div>
                    <div class="gap-2 mt-1">
                        <span class="text-xs font-bold uppercase">Straff</span><br />
                        <input type="number" class="form-input rounded-md bg-gray-100 border-transparent w-full" v-model="shiftEdit.max_shifts_penalty" />
                    </div>
                </div>
                <div class="grid grid-cols-2 gap-2">
                    <div class="gap-2 mt-1">
                        <span class="text-xs font-bold uppercase">Minst skift/vecka</span><br />
                        <input type="number" class="form-input rounded-md bg-gray-100 border-transparent w-full" v-model="shiftEdit.min_shifts" />
                    </div>
                    <div class="gap-2 mt-1">
                        <span class="text-xs font-bold uppercase">Straff</span><br />
                        <input type="number" class="form-input rounded-md bg-gray-100 border-transparent w-full" v-model="shiftEdit.min_shifts_penalty"/>
                    </div>
                </div>
                <div class="mt-2">
                    <span class="text-xs font-bold uppercase">Förklaringar:</span>
                    <p class="text-xs font-thin"><span class="font-bold">Straff vid överbokningar</span> beskriver hur mycket programmet straffar att det är fler resurser än önskat planerat på ett skift. <span class="font-bold">Straff 0</span> anger att skiftet ej kan överbokas.<br /><span class="font-semibold">Ex.</span> Om skift A har 4p straff för överbokningar och skift C har 8p straff för överbokningar kommer programmet välja att överboka skift A innan det överbokar skift C eftersom det blir &quot;dyrare&quot; att överboka skift A.</p>
                    <p class="text-xs font-thin mt-1"><span class="font-bold">Max skift/vecka</span> anger hur många skift en enskild resurs kan göra som mest av skiftet, <span class="font-semibold">Ex.</span> kan man använda detta för att begränsa antalet kvällspass en resurs kan göra på en vecka.</p> 
                    <p class="text-xs font-thin mt-1"><span class="font-bold">Minst skift/vecka</span> anger hur många skift en enskild resurs måste göra som minst av skiftet, <span class="font-semibold">Ex.</span> en resurs måste göra minst ett kvällspass per vecka.</p>
                </div>
            </div>
            
            <div class="col-span-2">
                <Button class="w-full" severity="danger" label="Ta bort" @click="deleteShift(shiftEdit.index)" />
            </div>
            <div class="col-span-4">

            </div>
            <div class="col-span-2">
                <Button class="w-full" severity="secondary" label="Avbryt" @click="showAdvanced=false" />
            </div>
            <div class="col-span-2">
                <Button class="w-full" label="Spara" @click="saveShift(shiftEdit.index)" />
            </div>
        </div>
    </div>
</template>