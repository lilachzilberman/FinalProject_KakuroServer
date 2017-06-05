package colman66.kakuro.server;

import com.fasterxml.jackson.core.*;
import com.fasterxml.jackson.databind.*;
import com.fasterxml.jackson.databind.node.*;
import java.io.*;
import java.nio.file.*;
import java.util.*;
import org.apache.commons.fileupload.*;
import org.apache.commons.io.*;

public class ImageProcessing {
  final static ObjectMapper mapper = new ObjectMapper();

  public static JsonNode getBoardFromImage(FileItem image) throws JsonProcessingException, IOException
  {
    Map<String, String> env = System.getenv();
    String pythonScript = env.get("KAKURO_PYTHON_MAIN");
    String pythonBin = env.containsKey("PYTHON3_BIN") ? env.get("PYTHON3_BIN") : "python3";
    if (pythonScript == null) {
      return mapper.readTree("[[\"X\"]]");
    }

    if (!Files.exists(FileSystems.getDefault().getPath(pythonScript))) {
      throw new RuntimeException("Expected KAKURO_PYTHON_MAIN (" + pythonScript + ") to be a file");
    }

    ProcessBuilder pb = new ProcessBuilder(pythonBin, pythonScript);
    Process p = pb.start();
    return mapper.readTree(p.getInputStream());
  }
}