Imports System.Security.Cryptography
Imports System.Text
Imports CryptSharp

''' <summary>
''' NavicatEncrypt will encrypt and decrypt the database passwords stored in the registry used by Navicat.
'''
''' This is a port to .net from the original Python3 code made by DoubleLabyrinth
''' Original repository https://github.com/DoubleLabyrinth/how-does-navicat-encrypt-password
''' 
''' You may use this code in any way as you see fit but give at least credits to the original creator
''' 
''' Ported by: CMBSolutions
''' Dependencies: CryptSharp by Chris McKee https://github.com/ChrisMcKee/cryptsharp 
''' </summary>
Public Class NavicatEncrypt
    Private Const NavicatCode As String = "3DC5CA39"
    Private _key As Byte()
    Private _iv As Byte()
    Private _cipher As Utility.BlowfishCipher

    Public Sub New()
        Try
            InitCipher()
            InitIV()
        Catch ex As Exception
            Throw ex
        End Try
    End Sub

    Private Sub InitCipher()
        Try
            Using hasher As SHA1 = SHA1.Create
                _key = hasher.ComputeHash(Encoding.ASCII.GetBytes(NavicatCode))
                _cipher = Utility.BlowfishCipher.Create(_key)
            End Using
        Catch ex As Exception
            Throw New CryptographicException("Error during cipher initialization")
        End Try
    End Sub

    Private Sub InitIV()
        Try
            _iv = {255, 255, 255, 255, 255, 255, 255, 255}
            _cipher.Encipher(_iv, 0, _iv, 0)
        Catch ex As Exception
            Throw New CryptographicException("Error during IV initialization")
        End Try
    End Sub

    Private Sub XorBytes(ByRef a As Byte(), ByVal b As Byte())
        For i As Integer = 0 To a.Length - 1
            a(i) = a(i) Xor b(i)
        Next
    End Sub

    Private Sub XorBytes(ByRef a As Byte(), ByVal b As Byte(), l As Integer)
        For i As Integer = 0 To l - 1
            a(i) = a(i) Xor b(i)
        Next
    End Sub

    Public Function Encrypt(inputString As String) As String
        Try
            Dim inData As Byte() = Encoding.ASCII.GetBytes(inputString)
            Dim outData As Byte() = Encrypt(inData)

            Dim outString As String = ""

            For Each dec In outData
                outString &= dec.ToString("X2")
            Next

            Return outString

        Catch ex As Exception
            Throw ex
        End Try
    End Function

    Private Function Encrypt(inData As Byte()) As Byte()
        Try
            Dim CV(_iv.Length - 1) As Byte
            Dim ret(inData.Length - 1) As Byte
            Dim left As Integer

            Dim rounded As Integer = Math.DivRem(inData.Length, 8, left)

            Array.Copy(_iv, CV, _iv.Length)

            For Each i In Enumerable.Range(0, rounded)
                Dim tmp(7) As Byte
                Array.Copy(inData, i * 8, tmp, 0, 8)

                XorBytes(tmp, CV)

                _cipher.Encipher(tmp, 0, tmp, 0)

                XorBytes(CV, tmp)

                For j = 0 To tmp.Length - 1
                    ret(i * 8 + j) = tmp(j)
                Next
            Next


            If left <> 0 Then
                _cipher.Encipher(CV, 0, CV, 0)

                Dim tmp(left - 1) As Byte

                Array.Copy(inData, rounded * 8, tmp, 0, left)
                XorBytes(tmp, CV, left)

                For j As Integer = 0 To tmp.Length - 1
                    ret(rounded * 8 + j) = tmp(j)
                Next
            End If

            Return ret

        Catch ex As Exception
            Throw ex
        End Try
    End Function

    Public Function Decrypt(hexString As String) As String
        Try
            Dim inData((hexString.Length / 2) - 1) As Byte

            For i As Integer = 0 To (hexString.Length / 2) - 1
                inData(i) = CByte("&H" & hexString.Substring(i * 2, 2))
            Next

            Dim outData As Byte() = Decrypt(inData)

            Dim outString As String = Encoding.ASCII.GetString(outData)

            Return outString
        Catch ex As Exception
            Throw ex
        End Try
    End Function

    Private Function Decrypt(inData As Byte()) As Byte()
        Try
            Dim CV(_iv.Length - 1) As Byte
            Dim ret(inData.Length - 1) As Byte
            Dim left As Integer

            Dim rounded As Integer = Math.DivRem(inData.Length, 8, left)

            Array.Copy(_iv, CV, _iv.Length)

            For Each i In Enumerable.Range(0, rounded)
                Dim tmp(7) As Byte
                Array.Copy(inData, i * 8, tmp, 0, 8)

                _cipher.Decipher(tmp, 0, tmp, 0)

                XorBytes(tmp, CV)

                For j = 0 To tmp.Length - 1
                    ret(i * 8 + j) = tmp(j)
                Next

                For j = 0 To CV.Length - 1
                    CV(j) = CV(j) Xor inData(i * 8 + j)
                Next
            Next

            If left <> 0 Then
                _cipher.Encipher(CV, 0, CV, 0)

                Dim tmp(left - 1) As Byte

                Array.Copy(inData, rounded * 8, tmp, 0, left)
                XorBytes(tmp, CV, left)

                For j As Integer = 0 To tmp.Length - 1
                    ret(rounded * 8 + j) = tmp(j)
                Next
            End If

            Return ret
        Catch ex As Exception
            Throw ex
        End Try
    End Function
End Class
