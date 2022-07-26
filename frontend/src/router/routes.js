import Index from "../views/Index.vue";

const routes = [
  {
    path: "/",
    name: "Index",
    component: Index,
  },
  {
    path: "/overview",
    name: "Overview",
    // route level code-splitting
    // this generates a separate chunk (module_name.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: () => import("../views/explorer/Overview.vue"),
  },
  {
    path: "/editor",
    name: "Editor",
    component: () => import("../views/label/Editor.vue"),
  },
];

export default routes;