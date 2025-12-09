import javax.crypto.Cipher;
import javax.crypto.SecretKey;
import javax.crypto.spec.IvParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import java.security.Key;
import java.util.Base64;

public class Main {
    public static void main(String[] args) throws Exception {
        String message = "Hello, World!";
        String password = "mysecretpassword";
        System.out.println(encrypt(message, password));
    }

    public static String encrypt(String message, String password) throws Exception {
        // Generate a random 128-bit IV
        byte[] iv = new byte[16];
        java.security.SecureRandom.getInstanceStrong().nextBytes(iv);

        // Create a SecretKeySpec from the password
        Key key = new SecretKeySpec(password.getBytes(), "AES");

        // Create an IvParameterSpec from the IV
        IvParameterSpec ivParam = new IvParameterSpec(iv);

        // Create a Cipher instance
        Cipher cipher = Cipher.getInstance("AES/CBC/NoPadding");
        cipher.init(Cipher.ENCRYPT_MODE, key, ivParam);

        // Encrypt the message
        byte[] encryptedMessage = cipher.doFinal(message.getBytes());

        // Return the IV and encrypted message as a single string, separated by a colon
        return Base64.getEncoder().encodeToString(iv) + ":" + Base64.getEncoder().encodeToString(encryptedMessage);
    }
}
