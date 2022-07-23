module.exports = {
  publicPath: process.env.NODE_ENV === "production" ? "/artonlabel/" : "/",
  outputDir: "dist",
  devServer: {
    port: 8081,
    https: false,
    open: false,
  },
};
