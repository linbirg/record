<template>
  <div>
    <section class="real-app" v-show="chatVisible">
      <Chat></Chat>
    </section>
    <div 
      class="toggle-btn"
      @click="toggleChat"
      :title="chatVisible ? '折叠' : '展开'"
    >
      <span class="icon" :class="chatVisible ? 'collapse' : 'expand'">
        {{ chatVisible ? '>' : '⋮' }}
      </span>
    </div>
  </div>
</template>

<script>
import Chat from "./ChatList/chat";
import { mapState } from "vuex";

export default {
  name: 'RightSide',
  components: {
    Chat,
  },
  computed: {
    ...mapState(['chatVisible']),
  },
  methods: {
    toggleChat() {
      this.$store.commit('setChatVisible', !this.chatVisible);
    },
  },
};
</script>

<style lang="scss" scoped>
.real-app {
  position: fixed;
  top: 72px;
  left: 1335px;
  width: 500px;
  height: calc(100vh - 72px - 20px);
  margin: 0 auto;
  font-size: 14px;
}

.toggle-btn {
  position: fixed;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 28px;
  height: 56px;
  background: rgba(156, 163, 175, 0.25);
  border-radius: 4px 0 0 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.2s;
  z-index: 1000;

  &:hover {
    background: rgba(59, 130, 246, 0.25);

    .icon {
      color: #3b82f6;
    }
  }

  .icon {
    font-size: 20px;
    color: #9ca3af;
    line-height: 1;
    font-weight: 600;
  }

  .collapse {
    font-size: 18px;
    font-weight: 400;
  }

  .expand {
    font-size: 18px;
    font-weight: 400;
  }
}
</style>
