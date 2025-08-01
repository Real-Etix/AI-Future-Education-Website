import { b as chatList, c as createElementBlock, a as createBaseVNode, F as Fragment, r as renderList, d as resolveComponent, o as openBlock, t as toDisplayString, e as createBlock, w as withCtx, _ as _export_sfc } from "./index-entry.js";
const _sfc_main = {
  data() {
    return {
      chatList
    };
  },
  computed: {
    sortedChatList: {
      get() {
        const today = /* @__PURE__ */ new Date();
        const todayDate = new Date(today.getFullYear(), today.getMonth(), today.getDate());
        const yesterdayDate = new Date(today.getFullYear(), today.getMonth(), today.getDate() - 1);
        const sorted = [...this.chatList].sort((a, b) => b.lastUpdated - a.lastUpdated);
        return sorted.reduce((acc, item) => {
          let comparingDate = new Date(
            item.lastUpdated.getFullYear(),
            item.lastUpdated.getMonth(),
            item.lastUpdated.getDate()
          );
          let dateVisual;
          if (comparingDate.getTime() === todayDate.getTime()) {
            dateVisual = "今日";
          } else if (comparingDate.getTime() === yesterdayDate.getTime()) {
            dateVisual = "昨日";
          } else {
            dateVisual = item.lastUpdated.getFullYear() == (/* @__PURE__ */ new Date()).getFullYear() ? "" : item.lastUpdated.getFullYear() + "年";
            dateVisual += item.lastUpdated.getMonth() + 1 + "月" + item.lastUpdated.getDate() + "日";
          }
          if (!acc[dateVisual]) {
            acc[dateVisual] = [];
          }
          acc[dateVisual].push(item);
          return acc;
        }, {});
      }
    }
  }
};
const _hoisted_1 = { class: "history-page" };
const _hoisted_2 = { class: "chat" };
const _hoisted_3 = { class: "date" };
const _hoisted_4 = { class: "name" };
function render(_ctx, _cache, $props, $setup, $data, $options) {
  const _component_router_link = resolveComponent("router-link");
  return openBlock(), createElementBlock("main", _hoisted_1, [
    _cache[1] || (_cache[1] = createBaseVNode("h2", null, "歷史會話", -1)),
    (openBlock(true), createElementBlock(Fragment, null, renderList(_ctx.sortedChatList, (chats, key) => {
      return openBlock(), createElementBlock("div", _hoisted_2, [
        createBaseVNode("h3", _hoisted_3, toDisplayString(key), 1),
        (openBlock(true), createElementBlock(Fragment, null, renderList(chats, (chat) => {
          return openBlock(), createBlock(_component_router_link, {
            class: "button",
            to: chat.link
          }, {
            default: withCtx(() => [
              createBaseVNode("div", _hoisted_4, [
                createBaseVNode("span", null, toDisplayString(chat.name), 1)
              ]),
              _cache[0] || (_cache[0] = createBaseVNode("div", { class: "content" }, " 唧唧復唧唧，木蘭當戶織。不聞機杼聲，唯聞女歎息。 問女何所思，問女何所憶。「女亦無所思，女亦無所憶。昨夜 見軍帖，可汗大點兵。軍書十二卷，卷卷有爺名。阿爺無大 兒，木蘭無長兄。願為市鞍馬，從此替爺征。」 東市買駿馬，西市買鞍韉，南市買轡頭，北市買長鞭。 旦辭爺娘去，暮宿黃河邊；不聞爺娘喚女聲，但聞黃河流水 鳴濺濺。旦辭黃河去，暮宿黑山頭；不聞爺娘喚女聲，但聞 燕山胡騎聲啾啾。 ", -1))
            ]),
            _: 2,
            __: [0]
          }, 1032, ["to"]);
        }), 256))
      ]);
    }), 256))
  ]);
}
const History = /* @__PURE__ */ _export_sfc(_sfc_main, [["render", render], ["__scopeId", "data-v-adf4c5e4"]]);
export {
  History as default
};
