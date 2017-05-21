package colman66.kakuro.server;

import ratpack.server.RatpackServer;
import ratpack.server.BaseDir;

public class Main {
  public static void main(String... args) throws Exception {
    RatpackServer.start(server -> {
      server.serverConfig(builder -> builder.baseDir(BaseDir.find(".ratpack.base.dir")))
        .handlers(chain -> chain.post("solveFromImage", new SolveFromImageHandler())
            .post("solveFromJson", new SolveFromJsonHandler())
            .files(f -> f.dir("public").indexFiles("index.html")));
    });
  }
}