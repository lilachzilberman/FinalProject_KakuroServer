package colman66.kakuro.server;

import static spark.Spark.*;

public class Main {
  public static void main(String... args) throws Exception {
    staticFiles.location("/public");
    post("/solveFromImage", new SolveFromImageHandler());
    post("/solveFromJson", new SolveFromJsonHandler());
  }
}