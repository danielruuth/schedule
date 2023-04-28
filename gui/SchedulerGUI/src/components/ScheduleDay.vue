<template>
    
    <div @mouseover="highlitePeerDays()" @contextmenu="onDayRightClick" class="day-info gridgap-1" :class="(missScheduled) ? 'request-missmatch dayIndex-' + dayIndex : 'dayIndex-' + dayIndex ">
        <div v-if="missScheduled" class="text-lg font-bold text-center mt-1 mb-1 h-full" :style="{backgroundColor: `${backgroundColor}`, backgroundImage: `${missScheduledBackground}`}">
                {{ shortname }}
        </div>
        <div v-else :style="{backgroundColor: `${backgroundColor}`}" :class="`text-lg font-bold text-center mt-1 mb-1 h-full`">
            {{ shortname }}

        </div>
    </div>
</template>
<script setup>
import {ref, watch, computed} from 'vue'
const props = defineProps({
    shifts: Array,
    dayOfWeek:Number,
    scheduledShift:Object|String,
    requestedShift:Object|Boolean,
    dayIndex:Number
})

const emit = defineEmits(['showContextMenu']) //defineEmits(['ResourceRequest'])

const backgroundColor = computed(()=>{
    if(props.scheduledShift && props.scheduledShift.color){
        return `#${props.scheduledShift.color}`
    }else if(props.requestedShift != ''){
        return `#${props.requestedShift.color}`
    }else{
        return 'rgba(255,255,255,0)'
    }
})

const missScheduled = computed(()=>{
    if((props.scheduledShift !='' && props.requestedShift!='') && props.requestedShift.shift != props.scheduledShift.name ){
        return true
    }else{
        return false
    }
})

const missScheduledBackground = computed(()=>{
    try{
        let desiredColor = props.shifts.filter(shift => props.requestedShift.shift == shift.name)[0].color
        let scheduledColor = props.scheduledShift.color

        return `linear-gradient(45deg, #${desiredColor} 50%, #${scheduledColor} 50%)`
    }catch(e){
        console.log(e)
        return '';
    }

})

const shortname = computed(()=>{
    if((props.scheduledShift !='' && props.requestedShift!='') && props.requestedShift.shift != props.scheduledShift.name ){
        return props.scheduledShift.name.substring(0,1) + '/' + props.requestedShift.shift.substring(0,1)
    }else if(props.scheduledShift !='' && props.requestedShift!=''){
        return props.scheduledShift.name.substring(0,1)
    }else if(props.scheduledShift!=''){
        return props.scheduledShift.name.substring(0,1)
    }else if(props.requestedShift != ''){
        return props.requestedShift.shift.substring(0,1) 
    }else{
        return '';
    }
})

const highlitePeerDays = function(){
    //Remove prev. highlite
    let highlitedElements = [].slice.call(document.getElementsByClassName( 'day-info'))
    let highlitedElementsLength = highlitedElements.length
    //Set new highlite
    let toBeHighlited = [].slice.call(document.getElementsByClassName( 'dayIndex-' + props.dayIndex ))
    let toBeHighlitedLength = toBeHighlited.length

    for(let r = 0; r < highlitedElementsLength; r++){
        highlitedElements[r].classList.remove('highlite-row-class')
    }

    for(let r = 0; r < toBeHighlitedLength; r++){
        toBeHighlited[r].classList.add('highlite-row-class')
    }
}

const onDayRightClick = (event) => {
    emit('showContextMenu', event, { dayIndex: props.dayIndex } )
};


</script>
<style>
    .highlite-row-class{
        background-color: rgba(255, 209, 0, .2);
    }
    .day-info{
        width:100%;
        height:100%;
        user-select: none;
        text-align:center;
    }
    .day-info div{
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .day-info div:first-child{
        border-radius: 2px;
        margin: 0 2px 0 2px;
    }

    .desired{
        background-image: linear-gradient(30deg, #013A6B 50%, #004E95 50%);
    }

    .request-missmatch{
        animation-name: color;
        animation-duration: 2s;
        animation-iteration-count: infinite;
        opacity:1;
    }

    @keyframes color {
    0% {
        opacity:1
    }
    50% {
        opacity:0.6
    }
    100% {
        opacity:1
    }
    }

</style>