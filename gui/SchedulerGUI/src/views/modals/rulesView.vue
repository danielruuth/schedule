<script setup>
    import {ref, inject} from 'vue'
    import ViewMore from '../../components/ViewMore.vue';
    const dialogRef = inject('dialogRef')
    const emit = defineEmits(['UpdateRules'])

    console.log(dialogRef.value.data.rules.health)

    const health = ref(dialogRef.value.data.rules.health || false)
    const groupOffshift = ref(dialogRef.value.data.rules.group_offshift || false)
    const weekendsConcat = ref(dialogRef.value.data.rules.min_weekends || false)
    const availableShifts = ref(dialogRef.value.data.shifts || [])

    const adv_shift = ref()
    const adv_type = ref()
    const adv_constraint = ref([0,0,0,0,0,0])

    const updateSettings = function(event){
        console.log('Updating rules', health, groupOffshift)
        emit('UpdateRules', {'health': health, 'min_weekends': false, 'group_offshift': groupOffshift})
    }

    const explain = function(type){
        const details = {
            "weekly_sum_constraint":"Bada bing",
            "shift_constraint":[
                'Hur många skift skall varje resurs göra som minst och som mest?',
                'Du anger minst och flest antal skift med två värden, s.k. mjuka och hårda gränser:',
                'Du kan se det som att mjuka värden är det önskade värdet, hårda är det som inte för överträdas.',
                '<b>Ex.</b> Du vill att varje resurs ska göra minst 2 kvällspass i veckan, hårt min sätts då till 2, skulle det vara ok att en resurs endast gör en kväll så gör vi mjukt min till 1.',
                '<b>Överträdelse</b> är hur programmet skall räkna ut vilket schema som uppfyller flest krav, står programmet inför två alternativ till att lösa en schemaläggning väljer den alltid den lösningen som &quot;kostar&quot; minst, så högre överträdelse = viktigare regel'
            ]
        }

        return details[type]
    }

</script>
<template>
    <div class="grid gap-1 gap-y-4 grid-cols-10 gap-x-2">
        <div class="col-span-5">
            <span class="text-xs font-bold uppercase">Används hälsoschema </span><br />
            <span class="text-xs font-light">Sätt regler efter hälsoschema-modellen, läs mer <a href="https://skr.se/skr/arbetsgivarekollektivavtal/arbetstid/dygnsvila.68896.html">här</a>.</span><br />
            <InputSwitch class="mt-4" v-model="health" @change="updateSettings($event)"/>
        </div>
        <div class="col-span-5">
            <span class="text-xs font-bold uppercase">Sammanhängande ledighet</span><br />
            <span class="text-xs font-light">Ha alltid två dagars sammanhållande ledighet</span><br />
            <InputSwitch class="mt-4" v-model="groupOffshift" @change="updateSettings($event)" />
        </div>
        <div class="col-span-10">
            <ViewMore :labels="['avancerat','dölj']" :hint="true" :hintHeight="50">
                <template #content>
                    <div class="col-span-10">
                        <span class="font-bold text-sm">Avancerat</span>
                    </div>
                    <div class="col-span-5">
                        <span class="font-bold text-xs">Typ</span>
                        <select name="shift" v-model="adv_type" class="form-input rounded-md bg-gray-100 border-transparent w-full">
                            <option value="weekly_sum_constraint">Begränsning veckototalsumma </option>
                            <option value="shift_constraint">Begränsning per skift</option>
                        </select>
                    </div>
                    <div class="col-span-5">
                        <span class="font-bold text-xs">Förklaring {{ adv_type }}</span>
                        <p v-for="paragraph in explain(adv_type)" class="text-xs font-thin mb-2" v-html="paragraph"></p>
                    </div>
                    <div class="col-span-4">
                        <span class="font-bold text-xs">Skift</span>
                        <select name="shift" v-model="adv_shift" class="form-input rounded-md bg-gray-100 border-transparent w-full">
                                <option v-for="(shift,index) in availableShifts" :value="index">{{ shift.name }}</option>
                        </select>
                    </div>
                    <div class="col-span-2">
                        <span class="font-bold text-xs">Hårt min.</span>
                        <input type="number" name="soft_min" v-model="adv_constraint[0]" class="form-input rounded-md bg-gray-100 border-transparent w-full"/>
                    </div>
                    <div class="col-span-2">
                        <span class="font-bold text-xs">Mjukt min.</span>
                        <input type="number" name="soft_min" v-model="adv_constraint[1]" class="form-input rounded-md bg-gray-100 border-transparent w-full" />
                    </div>
                    <div class="col-span-2">
                        <span class="font-bold text-xs">Överträdelse min</span>
                        <input type="number" name="soft_min" v-model="adv_constraint[2]" class="form-input rounded-md bg-gray-100 border-transparent w-full" />
                    </div>
                    <div class="col-span-4"></div>
                    <div class="col-span-2">
                        <span class="font-bold text-xs">Hårt max.</span>
                        <input type="number" name="soft_min" v-model="adv_constraint[3]" class="form-input rounded-md bg-gray-100 border-transparent w-full" />
                    </div>
                    <div class="col-span-2">
                        <span class="font-bold text-xs">Mjukt max.</span>
                        <input type="number" name="soft_min" v-model="adv_constraint[4]" class="form-input rounded-md bg-gray-100 border-transparent w-full" />
                    </div>
                    <div class="col-span-2">
                        <span class="font-bold text-xs">Överträdelse max</span>
                        <input type="number" name="soft_min" v-model="adv_constraint[5]" class="form-input rounded-md bg-gray-100 border-transparent w-full" />
                    </div>
                    <div class="col-span-10">
                        <span class="font-bold text-xs">&nbsp; </span>
                        <Button label="Lägg till avancerad regel" class="w-full" />
                    </div>
                </template>
            </ViewMore>
        </div>
    </div>
</template>