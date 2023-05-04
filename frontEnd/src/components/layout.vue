<template>
  <div>
    <Sidebar></Sidebar>
    <Container></Container>
    <RightSide></RightSide>
  </div>
</template>

<script>
import Sidebar from './sidebar'
import Container from './Container/container'
import RightSide from './RightSide'

export default {
  components: {
    Sidebar,
    Container,
    RightSide
  }
}
</script>