package colman66.kakuro.server;

import ratpack.handling.Handler;
import ratpack.handling.Context;
import static ratpack.jackson.Jackson.jsonNode;
import com.fasterxml.jackson.databind.node.ArrayNode;

import static ratpack.jackson.Jackson.json;

public class SolveFromJsonHandler implements Handler {
  public void handle(Context context) throws Exception {
    context.parse(jsonNode()).then(boardJson -> {
      KakuroSolver solver = new KakuroSolver((ArrayNode) boardJson);
      context.render(json(solver.getSolvedJson()));
    });
  }
}