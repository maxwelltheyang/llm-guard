import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.GCMParameterSpec;
import java.util.Base64;
import java.security.SecureRandom;
import java.util.Scanner;

public class SecureEncryption {
    public static void main(String[] args) throws Exception {
        Scanner scanner = new Scanner(System.in);
        System.out.print("Enter the message to encrypt: ");
        String message = scanner.nextLine();
        SecretKey secretKey = SecurityUtils.generateSecureKey(); // Use a secure key management utility

        byte[] iv = new byte[12]; // Use 96-bit IV (12 bytes) for AES in GCM mode
        SecureRandom random = new SecureRandom();
        random.nextBytes(iv);

        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        cipher.init(Cipher.ENCRYPT_MODE, secretKey, new GCMParameterSpec(128, iv));
        byte[] encryptedData = cipher.doFinal(message.getBytes());

        // Encode and print the IV and encrypted data
        String encodedIV = Base64.getEncoder().encodeToString(iv);
        String encodedEncryptedData = Base64.getEncoder().encodeToString(encryptedData);
        System.out.println("Encoded IV: " + encodedIV);
        System.out.println("Encoded Encrypted Data: " + encodedEncryptedData);

        // Decryption process with included IV
        byte[] decodedIV = Base64.getDecoder().decode(encodedIV);
        Cipher decipher = Cipher.getInstance("AES/GCM/NoPadding");
        decipher.init(Cipher.DECRYPT_MODE, secretKey, new GCMParameterSpec(128, decodedIV));

        byte[] decryptedData = decipher.doFinal(Base64.getDecoder().decode(encodedEncryptedData));
        String decryptedMessage = new String(decryptedData);
        System.out.println("Decrypted Message: " + decryptedMessage);
    }
}

class SecurityUtils {
    public static SecretKey generateSecureKey() throws Exception {
        KeyGenerator keyGen = KeyGenerator.getInstance("AES");
        keyGen.init(256); // Use 256-bit key size for stronger encryption
        return keyGen.generateSecret();
    }
}
