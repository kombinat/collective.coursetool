process.traceDeprecation = true;
const mf_config = require("@patternslib/dev/webpack/webpack.mf");
const path = require("path");
const package_json = require("./package.json");
const package_json_patternslib = require("@patternslib/patternslib/package.json");
const webpack_config = require("@patternslib/dev/webpack/webpack.config").config;

module.exports = () => {
    let config = {
        entry: {
            "coursetool.min": path.resolve(__dirname, "resources/index"),
        },
    };

    config = webpack_config({
        config: config,
        package_json: package_json,
    });
    config.output.path = path.resolve(__dirname, "src/collective/coursetool/browser/static");

    // config.module.rules.push({
    //     test: /\.svg$/i,
    //     type: 'asset/resource',
    // });

    config.plugins.push(
        mf_config({
            name: "collective.coursetool",
            filename: "coursetool-bundle-remote.min.js",
            remote_entry: config.entry["coursetool.min"],
            dependencies: {
                ...package_json_patternslib.dependencies,
                ...package_json.dependencies,
            },
        })
    );

    if (process.env.NODE_ENV === "development") {
        config.devServer.port = "8011";
        config.devtool = "source-map";
        config.devServer.static.directory = __dirname;
    }

    // console.log(JSON.stringify(config, null, 4));

    return config;
};
